# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

_Inscrire la documentation technique_
## Prérequis
 - Docker
 - Python

## Lancement de la solution
 Docker compose permet de lancer l'ensemble du test incluant l'api, le serveur posgreSQL ansi que le pipeline ETL qui est executer tous les jours à minuit. 
Dans la racine du projet lancer: docker compose up
j'ai

Dev: Une version sans le scheduler peut etre lancée a l'aide de docker-compose.dev.yml. Cette version lance uniquement le serveur posgresql ansi que l'api. le pipeline etl peut ensuite etre testé direcemment:
```docker-compose -f docker-compose.dev.yml up```
```docker build -t moovitamix_etl .```
```docker run moovitamix_etl```

## Configuration
Les variables d'environnement sont dans en clair dans le docker compose. Il serait préférable d'utiliser un outil de gestion des parametres comme AWS Parameter store ou autres solution de gestion de configuration et de mots de passe.

## Tests
Installer les dépendences du projet:
```pip install -r requirements.txt -r```

Démarrer docker compose dev pour que l'api et que le serveur postgresSQL soient disponibles.
Démarrer l'execution des tests:

```pytest``

## Questions (étapes 4 à 7)

### Étape 4

Schema de la base de données

Table: tracks
-------------
- name: VARCHAR(255) - Nom de la chanson (clé primaire)
- artist: VARCHAR(255) - Artiste de la chanson
- songwriters: VARCHAR(255) - Auteurs/compositeurs de la chanson
- duration: VARCHAR(255) - Durée de la chanson
- album: VARCHAR(255) - Album auquel la chanson appartient
- genres: VARCHAR(255) - Genres musicaux associés à la chanson
- created_at: TIMESTAMP - Date et heure de création
- updated_at: TIMESTAMP - Date et heure de la dernière mise à jour
- run_id: VARCHAR(255) - Identifiant de l'exécution pour suivre les processus

---------------------------------------------------------
Table: users
-------------
- id: SERIAL - Identifiant unique de l'utilisateur (clé primaire)
- first_name: VARCHAR(255) - Prénom de l'utilisateur
- last_name: VARCHAR(255) - Nom de famille de l'utilisateur
- email: VARCHAR(255) - Adresse e-mail de l'utilisateur (unique)
- gender: VARCHAR(255) - Sexe de l'utilisateur
- favorite_genres: VARCHAR(255) - Genres musicaux préférés de l'utilisateur
- created_at: TIMESTAMP - Date et heure de création
- updated_at: TIMESTAMP - Date et heure de la dernière mise à jour
- run_id: VARCHAR(255) - Identifiant de l'exécution pour suivre les processus

---------------------------------------------------------
Table: listen_history
----------------------
- user_id: INT - Identifiant de l'utilisateur (clé étrangère vers la table `users`)
- items: JSONB - Liste des morceaux écoutés, stockée en format JSON
- created_at: TIMESTAMP - Date et heure de création de l'enregistrement
- updated_at: TIMESTAMP - Date et heure de la dernière mise à jour de l'enregistrement
- run_id: VARCHAR(255) - Identifiant de l'exécution pour suivre les processus

---------------------------------------------------------
Relations entre les tables
---------------------------
- La table `tracks` ne possède pas de relations directes avec les autres tables.
- La table `users` est liée à la table `listen_history` par la colonne `user_id`.


Choix de la base de données:
J'ai choisi PostgreSQL comme systeme de base de données relationelle. Il supporte des types de données avancés comme JSONB, ce qui est idéal pour stocker des informations flexibles, telles que les listes d'items présentes dans l'historique d'ecoute. De plus, il est extensible, performant et bien adapté pour des applications nécessitant des requêtes complexes.

### Étape 5

Il serait necessaire de mettre en place un systeme de surveillance continue pour assurer la santé du pipeline de données. l'objectif serait d'extraire différentes métrique sur les exection incluant la volumétrie des données extraites ainsi que le taux de réussite des exections. Une analyste des logs générées par chacunes des executions permeterais égalemment de comprendre les causes d'erreures. 


### Étape 6

Pour l'architecture du système de recommandation, je mettrai en place un processus automatisé pour calculer les recommandations chaque jour (en lot), en utilisant les données récentes apres la mise a jour du pipeline. Le réentrainement du modèle sera également automatisé, en définissant des critères (comme une période fixe ou un seuil de performance basé sur les données d'utilisation) pour lancer de nouveaux cycles de réentrainement sans intervention manuelle.

Les prédictions du modèle de recommendation seraient enregistrées quotidiennementmet disponibilisées pour leur utilisation . Une historisation des recomendations peut aussi etre utile pour de l'analyse et pour  

Etapes du processus: 
1. Ingestion:  Mise à jour quotidienne des données des utilisateurs (écoutes, interactions, préférences) via le pipeline ETL.

2. Prétraitement: Nettoyage, transformation et enrichissemment des données les caractéristiques (par exemple, encodage des genres musicaux, agrégation des comportements d’écoute).

3. Calcule des recommandations en exécutant un modèle en lot pour générer des suggestions personnalisées.

4. Enregistremment: Sauvegarde des recommandations en base de données ou dans un cache rapide comme Redis pour une récupération efficace.

5. Historisation: historisation des recommandations pour permettre une analyse et un suivi des performances (taux d’engagement, pertinence).

6. Automatisation et analyse: le réentrainement du modèle est déclenché à intervalles réguliers ou dès qu’une baisse des performances est détectée. Un suivi des performance et fait a l'aide de métriques définies.

### Étape 7

1. Surveillance des performances: 
- Mise en place des métriques de suivi (précision, rappel, NDCG, taux de clics, etc.).
- Analuse de l’évolution de métriques sur les recommandations produites.

2. Déclenchement
- Seuil de dégradation des performances (exemple : une baisse de x % sur une métrique)
- Il est égalment possible d'entrainer le modele a des intervalle réguliers

3. Préparation des données
- Récupération et nettoyage des nouvelles données du pipeline ETL.
- Mise à jour des features pour le modèle (normalisation, encodage, agrégation, etc).

4. Réentrainement du modèle
- Utilisation d'un outil de gestion de workflow pour l'entrainement (exemple : AWS SageMaker, Airflow).
- Évaluation du nouveau modèle avec des jeux de tests et le compare à la version actuelle.

5. Validation et déploiement
- Si le modèle amélioré dépasse le modèle actuel en performance, je le déploie en production.
- Sinon, l'ancien modèle est utilisé et les résultats du test sont sauvegardés.

7. Surveillance post-déploiement
- Evaluation de l'impact des nouvelles recommandations sur les utilisateurs.
- Assurer une amélioration continue avec une surveillance continue