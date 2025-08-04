# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_
N.B. La documentation se concentrera sur la gestion du flux de données sans l'API.

### Description de la solution 
Ce projet est un pipeline ETL (Extract, Transform, Load) containerisé, développé à l'aide de Python 3.11-slim et fonctionnant dans un environnement virtuel Docker. Ce choix est pour garantir un environnement cohérent et isolé pour l'exécution du pipeline ETL sur différents systèmes. Le but de ces travaux est d'automatiser l'ingestion, la transformation et le stockage des données selon un calendrier quotidien. Nous allons utiliser Airflow comme orchestrateur. Cet outil automatise et planifie des workflows de complexité variable. De cette manière, nous garantissons le bon fonctionnement des scripts Python, avec une gestion adéquate des dépendances et une surveillance facile et contrôlée à l'aide d'un système d'alerte et de relance. 

### Structure du projet 
<pre>
technical-test-data-engineer/
│
├── etl/                       # ETL scripts
│   ├── extract.py
│   ├── transform.py
│   └── load.py 
│
├── etltests/                 # Unit and integration tests
│   ├── pytest.ini
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
│
├── Dockerfile                 # Environment setup
│
├── docker-composer.yml        # Docker composer
│
├── dags/                      # Airflow DAGs
│   └── etl_daily_dag.py
│
└── requirements.txt           # Python dependencies
</pre>
### Outils et technologies
- **python:3.11-slim** (comme langage de programmation)
- **Docker** (comme environnement virtuel)
- **Pandas** pour la manipulation des données
- **Logging** pour la traçabilité
- **Pytest** pour les tests
- **Airflow** pour la planification et la tracabilité

### Structure de nos tables
**Tracks table**
| Field         | Type     | Description                                    |
|---------------|----------|--------------------------------------          |
| id            | INTEGER  | Primary key                                    |
| name          | TEXT     | Nom du morceau                                 |
| artist        | TEXT     | Nom de l'artiste                               |
| songwriters   | TEXT     | Auteur-compositeur                             |
| duration      | TEXT     | Durée du morceau (e.g. `21:33`)                |
| genres        | TEXT     | Genre(s)                                       |
| album         | TEXT     | Nom de l'album                                 |
| created_at    | TEXT     | Timestamp à la date de création du morceau     |
| updated_at    | TEXT     | Timestamp à la date du mise à jour du morceau  |

**Users table**
| Field            | Type     | Description                                         |
|------------------|----------|------------------------------------------           |
| id               | INTEGER  | Primary key                                         |
| first_name       | TEXT     | Prénom de l'utilisateur                             |
| last_name        | TEXT     | Nom de famille de l'utilisateur                     |
| email            | TEXT     | Adresse e-mail de l'utilisateur (doit être unique)  |
| gender           | TEXT     | Sexe de l'utilisateur                               |
| favorite_genres  | TEXT     | Genres préférés de l'utilisateur                    |
| created_at       | TEXT     | Timestamp à la date de l'utilisateur                |
| updated_at       | TEXT     | Timestamp à la date du mise à jour de l'utilisateur |


**Listen history table**
| Field             | Type     | Description                                             |
|--------------     |----------|---------------------------------------------------      |
| id                | INTEGER  | Auto-increment primary key                              |
| user_id           | INTEGER  | Foreign key referencing `users.id`                      |
| item_id           | INTEGER  | Foreign key referencing `tracks.id`                     |
| created_at        | TEXT     | Timestamp à la date de l'historique                     |
| updated_at        | TEXT     | Timestamp à la date du mise à jour de l'historique      |

### Les Commandes Docker

**Crée une image Docker pour lancer l'application**
<pre>
docker build -t technical-test-data-engineer .
</pre>
**Démarre et exécute les contenaires docker**
<pre>
docker-compose up --build
</pre>
**Démarre et exécute les contenaires docker pour l'api seulement**
<pre>
docker-compose up technical-test-data-engineer
</pre>
**arrêter l'exécution du contenaire docker**
<pre>
docker-compose stop
</pre>
**lancer les pytest dans contenaire docker**
<pre>
docker exec etl_job pytest -v test_real_api.py
</pre>

## Questions (étapes 4 à 7)

### Étape 4
**Détailler le schéma de la base de données que vous utiliseriez pour stocker les informations récupérées des trois sources de données mentionnées plus tôt. Quel système de base de données recommanderiez-vous pour répondre à ces besoins et pourquoi?**

Pour le schéma de la base de données, nous avons décidé d'utiliser une base de données relationnelle.
C'est un choix naturel, car un utilisateur peut écouter plusieurs morceaux et un morceau peut être écouté par plusieurs utilisateurs. Le tableau historique permet donc de relier tous ces éléments.

**Utilisation une base de données relationnelle**  
1. L'ingestion plus facile des données à l'aide de clés étrangères garantit la cohérence des liens entre les utilisateurs, les morceaux et l'historique d'écoute. 
2. Format structuré et fortement typé, idéal pour des données transactionnelles cohérentes.  
3. Avec un indexage approprié, même les tables relationnelles plus volumineuses s'adaptent bien à de nombreux cas d'utilisation.
4. Permet des requêtes efficaces, une extraction cohérente des caractéristiques et une intégration transparente avec les outils de science des données.

**Hébergement cloud**
1. Évolutivité
2. Disponibilité et sauvegardes
3. Accès et sécurité
4. Aucune charge de maintenance

**SQLite pour les tests**
1. Local et sans installation supplémentaire
2. Adapté pour les pipelines CI/CD et le développement local
3. Compatible avec SQL dans le futur
4. Coût nul

### Étape 5 : 
**Le client exprime le besoin de suivre la santé du pipeline de données dans son exécution quotidienne. Expliquez votre méthode de surveillance à ce sujet et les métriques clés.**

La qualité des données est l'une de nos priorités. C'est pourquoi nous avons fait plusieurs choix dans la manière dont nous gérons notre flux de données afin d'en garantir la qualité. Cela inclut l'utilisation d'Airflow comme orchestrateur de tâches, car il fournit des alertes intégrées, des rappels en cas d'échec et des journaux. Nous avons également choisi de mettre en œuvre plusieurs règles dans le processus ETL afin de vérifier que les bonnes données sont intégrées dans nos systèmes. Nous pouvons également mettre en œuvre des procédures de validation des données directement dans nos bases de données SQL. Nous avons également envisagé des processus pour alimenter et réentraîner notre modèle ML. Nous vous donnerons plus de détails à ce sujet dans les prochaines parties.

### Étape 6
**Dessinez et/ou expliquez comment vous procèderiez pour automatiser le calcul des recommandations.**

Nous automatiserons le calcul des nouvelles recommandations en alimentant le modèle pré-entraîné avec de nouvelles données (pistes, utilisateurs et historique des listes) générées quotidiennement, après avoir validé les données obtenues chaque jour via l'API du projet. Nous pouvons ajouter cette partie à notre processus Airflow. Nous nous concentrons sur les prédictions à faible latence et transmettons les résultats aux API.

### Étape 7
**Dessinez et/ou expliquez comment vous procèderiez pour automatiser le réentrainement du modèle de recommandation.**

Pour réentraîner notre modèle, nous préparons des données historiques (caractéristiques et étiquettes) afin de mettre à jour périodiquement le modèle lorsque les performances diminuent ou que de nouveaux modèles de comportement apparaissent. Il fonctionne moins fréquemment, une fois par mois par exemple. La fréquence est déterminée avec le Data Scientist en fonction de la précision actuelle du modèle de recommandation, des rappels et d'autres indicateurs. Cela nous aide à garantir la précision du modèle au fil du temps.