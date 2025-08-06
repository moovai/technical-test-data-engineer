# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_
etape 1:
utilisation de uv en installant une version 3.9 puis activation de cette environement : source .env_uv_3919/bin/activate
installation des paquets uv pip install -r requirements.txt

etape 2: 
lancement du serveur:
une erreur dans les methodes getters du main utilise la classe Page qui n'avait pas les methodes get_tracks, get_users et get_listen_history
modification du code en utilisant la classe CustomPage a la place de Page
le port 8000 etant occupe,
j'ai redirige en local le serveur sur le port 8001 avec python -m uvicorn main:app --port 8001

Le serveur demarre et l'url http://127.0.0.1:8001/docs affiche l'API

etape 3 :
je teste trois aspects :
- la reponse 200 du serveur
- la reponse en terme de data
- le schema de la data retourne

_Inscrire la documentation technique_

## Questions (étapes 4 à 7)

### Étape 4

nous partons de la data d'origine et du besoin de faire des recommandations a partir des chansons ecoutes.
une chanson seraecoute a une date d par un ou plusieurs users. Un user ecoutera une ou plusieurs chansons. En modele relationnel , nous aurions une table pivot qui correspondrait au coeur de ce qui va faire l'objet des calculs pour les recommandations : la table user_history.
Dans votre cas, la table d'association pourrait être `user_listen_history` (ou `ecoutes`):

**Tables principales :**

*   **`users`**
    *   `user_id` (PK)
    *   `user_name`
    *   ...

*   **`songs`**
    *   `song_id` (PK)
    *   `title`
    *   `artist`
    *   ...

**Table d'association :**

*   **`user_listen_history`**
    *   `listen_id` (PK, optionnel, mais bonne pratique pour une clé primaire unique)
    *   `user_id` (FK vers `users.user_id`)
    *   `song_id` (FK vers `songs.song_id`)
    *   `listen_timestamp` (Quand l'écoute a eu lieu - très important pour les recommandations basées sur l'historique récent)
    *   `play_duration_seconds` (Durée d'écoute, si pertinent)
    *   ...

Avec cette structure, vous pouvez facilement savoir quelles chansons un utilisateur a écoutées, et quels utilisateurs ont écouté une chanson donnée, ainsi que des détails sur chaque événement d'écoute.

Ainsi ce modele peut etre porte par un SGDBR comme Postgresql.

Les donnees massives issue de l'API , elles seraint stocker dans un data lake tel AWS S3.
Quand aux donnees issue des calculs de machine learning seraient stocker dans une base de donnees cle valeur comme MongoDB:
"Calcul des recommandations terminé et servi via MongoDB"
```

**Exemple de document dans MongoDB :**

```json
{
  "_id": "user_12345", // La clé est le user_id pour un lookup O(1)
  "recommendations": [
    "song_id_abc",
    "song_id_def",
    "song_id_ghi",
    // ...
  ],
  "model_version": "v1.2.3",
  "calculation_date": "2025-08-04T22:00:00Z"
}
```
ainsi , on a un workflow hybride Data lake de donnees massives sur un cloud  + les donnees maitres sur une base relationnelles + les resultats des calculs de recommandations fait a partir de  la table user_history_listen

### Étape 5

le systeme de surveillance de la sante  du pipel;ine va reposer sur :
1- un systeme de logging , etape par etape , de chaque composant du pipeline 
2- un dashboard via un outil BI pour visualiser les metriques ce qui permet d'avoir une big picture du pipeline
3- des alertes envoyeant aux intervenants cles lies aux actions cles du pipelines dans un canala specifique de communication(email, tchat ...)

venons en aux metriques:
- les metriques lie au pipeline , aux ressources materielles consommes, aux statutss desou ko des etapes du pipeline. 

- les metriques lie a la data : le nombre de lignes , la preence de null , la coherence du schema , les types de donnees



### Étape 6

Pour automatiser le calcul des recommandations de type scoring , je mettrais en place un workflow orchestré qui se déclenche après la réussite du pipeline d'ingestion de données.

**Architecture et Flux de Travail :**

```
[FIN du Pipeline d'Ingestion] -> [DÉCLENCHEMENT du Workflow de Calcul]
    |
    V
[1. Tâche de Calcul Batch (ex: Spark,..)]
    |   a. Charge le dernier modèle validé 
    |   b. Charge les nouvelles données d'historique des utilisateurs.
    |   c. Pour chaque utilisateur, calcule les N recommandations.
    |   d. Écrit les résultats dans une table "staging".
    |
    V
[2. Tâche de Validation des Résultats]
    |   a. Vérifie la qualité des recommandations (ex: nombre d'utilisateurs avec des recommandations, pas de valeurs nulles).
    |
    V
[3. Tâche de Keep or Replace]
    |   a. Si la validation est réussie, remplace l'ancienne table de recommandations par la nouvelle (staging).
    |   b. Archive l'ancienne table pour analyse.
    |
    V
[4. Notification] -> [Canal Slack/Email: "Calcul des recommandations terminé avec succès"]

### Étape 7

la le reentrainement du modele de recommandation va necessite d'evaluer  le modele existant et le modele issue de donnees  recentes. Ces evaluations vontse faire sur les metriques de performances des modeles selon un jeu de donnees test.

[DÉCLENCHEUR (ex: Hebdomadaire, ou baisse de performance)]
    |
    V
[1. Tâche d'Extraction et Préparation des Données]
    |   a. Crée un jeu de données d'entraînement (ex: 90 derniers jours) et de test (ex: 7 derniers jours).
    |
    V
[2. Tâche d'Entraînement Parallèle]
    |   a. Entraîne un nouveau "modèle candidat" sur le jeu de données d'entraînement.
    |
    V
[3. Tâche d'Évaluation Comparative]
    |   a. Charge le "modèle en production" actuel.
    |   b. Évalue le "modèle candidat" ET le "modèle en production" sur le même jeu de données de test.
    |   c. Compare leurs métriques de performance.
    |
    V
[4. Tâche de Validation et Enregistrement (Conditionnelle)]
    |   a. SI le candidat est meilleur que la production (selon un seuil défini, ex: +5% de précision):
    |      i.  Enregistre le "modèle candidat".
    |      ii. Attribue au nouveau modèle le tag "staging" ou "validation".
    |   b. SINON:
    |      i. Garde le modèle en production et alerte l'équipe (le modèle n'apprend plus).
    |
    V
[5. Tâche de Déploiement/Promotion (Manuelle ou Automatique)]
    |   a. Un Data Scientist valide les métriques du modèle en "staging".
    |   b. Promotion du modèle : le tag passe de "staging" à "production".
    |
    V
[6. Notification] -> [Rapport de réentraînement envoyé sur Slack/Email]
