# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

### 1- Préparer l'environnement Python
1.	Cloner le dépôt : après avoir forké le dépôt, clonez‑le sur votre machine locale.
2.	Créer un environnement virtuel compatible avec Python ≥ 3.9 et < 3.13. Par exemple :
    python3 -m venv .venv
    source .venv/bin/activate
3.	Installer les dépendances : un fichier requirements.txt est fourni. Exécutez :
    pip install -r requirements.txt
Cela installera notamment fastapi, uvicorn, requests, pydantic, faker et pytest.
### 2- Lancer l'API de test
L'application FastAPI servant les données se trouve dans src/moovitamix_fastapi. Pour la démarrer en local :
    cd src/moovitamix_fastapi
    python -m uvicorn main:app --reload
L'application se lance sur http://127.0.0.1:8000 et expose trois endpoints (/tracks, /users et /listen_history) paginés. Une fois le serveur démarré, la documentation interactive est accessible à http://127.0.0.1:8000/docs.
### 3- Exécuter le pipeline de récupération
Le script Python src/data_pipeline.py fournit un pipeline simple qui interroge chaque endpoint paginé et enregistre les données dans des fichiers JSONL datés. Par défaut il s’attend à ce que l’API soit disponible sur http://localhost:8000 et stocke les données dans un dossier output. Vous pouvez lancer une ingestion manuelle ainsi :
    python -m src.data_pipeline --base-url http://127.0.0.1:8000 --output-dir output
Cela téléchargera toutes les pages des trois endpoints et créera trois fichiers (par exemple : tracks_20250906.jsonl, users_20250906.jsonl et listen_history_20250906.jsonl) dans le répertoire output. 

### 4- Lancer les tests unitaires
Des tests unitaires sont fournis dans test/test_data_pipeline.py. Ils vérifient le comportement du pipeline sans nécessiter de serveur HTTP en utilisant des mocks. Depuis la racine du projet, exécutez :
    pytest
Pytest doit rapporter que tous les tests passent.
## Questions (étapes 4 à 7)

### Étape 4 : schéma de base de données et moteur recommandé
Pour stocker les données des trois sources, je propose une base relationnelle avec trois tables principales et une table de jonction normalisée :
--------
1.	Table tracks : stocke les métadonnées des chansons.
colonne	- type	- description
id (PK)	- integer	- identifiant unique de la chanson
name	- text	- nom de la chanson
artist	- text	- interprète principal
songwriters	- text	- auteurs/compositeurs
duration	- interval/time	- durée de la piste (ou nombre de secondes)
genres	- text	- genres principaux (concaténés ou en JSON)
album	- text	- album d’origine
created_at	- timestamp	- date de création de l’enregistrement
updated_at	- timestamp	- date de dernière mise à jour
---------
2.	Table users : informations sur les utilisateurs.
colonne	- type	- description
id (PK)	- integer	- identifiant unique de l’utilisateur
first_name	- text	- prénom
last_name	- text	- nom
email	- text	- adresse électronique unique
gender	- text	- genre (liste contrôlée)
favorite_genres	- text	- genres favoris (concaténés ou tableau JSON)
created_at	- timestamp	- date de création du compte
updated_at	- timestamp	- date de dernière mise à jour
---------
3.	Table listen_history : journal des écoutes individuelles, à granularité fine.
colonne	- type	- description
id (PK)	- serial	- identifiant interne de la ligne
user_id	- integer	- clé étrangère vers users.id
track_id	- integer	- clé étrangère vers tracks.id
played_at	- timestamp	- date/heure de l’écoute (issue de created_at de l’API)
updated_at	- timestamp	- date/heure de mise à jour (issue de updated_at de l’API)
---------
Les objets ListenHistoryOut retournés par l’API contiennent un champ items avec une liste d’IDs de chansons. Dans le schéma proposé, chaque ID est éclaté en une ligne distincte de listen_history afin de normaliser la relation « utilisateur ↔ piste ». Ce format facilite le calcul de matrices utilisateur/piste et l’application d’algorithmes de filtrage collaboratif. Pour les environnements de développement et de test, une base SQLite peut suffire. En production, je recommande PostgreSQL.


### Étape 5 : surveillance du pipeline de données et métriques clés
Un pipeline de production doit fournir de la visibilité et des alertes en cas d’anomalie. Voici une stratégie de surveillance :
1.	Orchestration : utilisez un orchestrateur (Airflow, Prefect ou Dagster) pour exécuter le pipeline quotidiennement. Ces outils historisent les exécutions et produisent des logs centralisés.
2.	Instrumenter le code : le pipeline src/data_pipeline.py génère déjà des logs via le module logging. En production, on peut envoyer ces logs vers un collecteur (CloudWatch).
3.	Metrics : exposez des compteurs et chronomètres:
    - Nombre d’enregistrements ingérés par endpoint (tracks, users, listen_history). Une variation inhabituelle (trop peu ou trop) peut signaler un problème.
    - Durée des appels et temps total du pipeline.
    - Taux de succès/erreur des requêtes HTTP et code de retour.
    - Volume de données écrites (taille des fichiers ou nombre de lignes).
    - Déduplication : nombre d’IDs déjà présents dans la base par rapport aux nouveaux.
4.	Alertes : configurez des seuils (par exemple, < 80 % de données attendues ou un code 5xx renvoyé par l’API) qui déclenchent des notifications (courriel, Slack, PagerDuty).
5.	Tableau de bord : regroupez ces métriques dans Grafana ou similar pour suivre l’évolution du pipeline dans le temps et investiguer rapidement en cas d’incident.


### Étape 6: automatisation du calcul des recommandations
Pour automatiser le calcul des recommandations, je propose une architecture par lots dont les grandes étapes sont :
1.	Ingestion des données : utiliser le pipeline décrit plus haut pour alimenter quotidiennement les tables users, tracks et listen_history.
2.	Préparation des données : créer une matrice utilisateur–piste à partir des historiques. On peut appliquer des heuristiques simples (compter le nombre d’écoutes par piste) ou des techniques de filtrage collaboratif (matrices creuses, factorisation matricielle). Par exemple :
    - Calculer un score d’intérêt score(u, t) basé sur la fréquence d’écoute, la récence et la similarité de genres.
    - Normaliser les scores pour éviter de privilégier uniquement les utilisateurs très actifs.
3.	Génération des recommandations : pour chaque utilisateur, sélectionner les N pistes avec les meilleurs scores qu’il n’a pas encore écoutées. Écrire ces recommandations dans une table recommendations avec les colonnes (user_id, track_id, score, generated_at).
4.	Orchestration : planifier ce job dans Airflow/Prefect après la fin de l’ingestion quotidienne. Les scientifiques des données peuvent versionner leur logique de recommandation (ex.: code Python ou notebook) et le pipeline exécutera toujours la dernière version validée.
5.	Exposition : l’API de l’application peut ensuite consommer la table recommendations pour personnaliser les playlists des utilisateurs.
Cette approche sépare clairement l’ingestion, le calcul et la restitution, ce qui facilite la maintenance. Pour de très grands volumes, il peut être judicieux d’utiliser Spark ou similar pour le calcul parallèle.

### Étape 7 : automatisation du réentraînement du modèle de recommandation
Lorsqu’un modèle d’apprentissage automatique est utilisé (par exemple, une factorisation de matrices ou un réseau de neurones pour des embeddings musicaux), il doit être réentraîné régulièrement afin de rester pertinent. Voici une proposition :
1.	Pipeline d’entraînement : créez un second DAG dans Airflow dédié au réentraînement. Il réalise les étapes suivantes :
    -	Extraction : lire les tables users, tracks et listen_history mises à jour.
    -	Prétraitement : préparer les données sous forme de couples (utilisateur, piste, label) ; par exemple, un label binaire indiquant si la piste a été écoutée.
    -	Feature engineering : ajouter des variables (genres, popularité de la piste, ancienneté du compte) pour enrichir le signal.
    -	Entraînement : entraîner le modèle de recommandation (algorithme de filtrage collaboratif, factorisation matricielle, ou modèle de deep learning). Utiliser des outils comme MLflow pour suivre les expériences, les hyperparamètres et les métriques (AUC, précision@k).
    -	Évaluation et validation : comparer les performances du nouveau modèle à celles du modèle actuel. Seul un modèle plus performant est promu.
    -	Déploiement : si le modèle est validé, enregistrer l’artefact dans un registre de modèles (MLflow Model Registry, S3, etc.) et mettre à jour le service de recommandations pour utiliser la nouvelle version.
2.	Déclencheurs : ce réentraînement peut être planifié à intervalles réguliers (par exemple, chaque semaine) et/ou déclenché par des événements (par exemple, lorsqu’un nombre suffisant de nouvelles écoutes est atteint ou lorsqu’une dérive de distribution est détectée sur les données d’entrée).
3.	Surveillance du modèle : collecter des métriques en production (taux de clics, temps d’écoute, satisfaction utilisateur) pour détecter une dégradation des performances et déclencher un réentraînement.

Cette automatisation garantit que le système de recommandation reste aligné sur les habitudes musicales des utilisateurs et évolue en même temps que le catalogue de titres.
