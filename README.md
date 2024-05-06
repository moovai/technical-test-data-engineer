# Objectif

Ce test est élaboré pour mettre en lumière votre expertise dans le domaine de l'ingénierie des données à travers l'utilisation du langage de programmation Python. Il vise également à évaluer votre capacité à soutenir les scientifiques des données dans le développement de solutions d'intelligence artificielle.

Le test se déroule en deux étapes:

1. Test technique: compléter les différentes sections de ce test décrites ci-dessous avant votre entretien.
2. Entretien collaboratif: présentation de vos réalisations lors de notre rencontre.

La phase de travail collaboratif a pour objectif de nous donner un aperçu de ce à quoi il serait de travailler ensemble et devrait être perçue comme un effort mutuelle. S'en terminera un échange d'expériences sur le test dans son ensemble.

# Prérequis

- Connaissance d'outils d'orchestration (e.g. Airlfow).
- Connaissance des APIs et de leurs protocoles.
- Connaissance des systémes de bases de données.
- Connaissance avancées de Python dans les domaines suivants: analyse, visualisation de données et tâches de script.

Veuillez noter que ce test technique ne nécessite *aucun frais* de votre part.

## Contexte

Le test technique évalue des aspects clés de l'ingénierie de données chez Moov AI : la conception et la mise en œuvre de flux de données pour alimenter des modèles, ainsi que le soutien aux scientifiques de données dans la mise en place de solutions de machine learning. Il ne se concentre pas sur les compétences spécifiques des outils, mais sur la compréhension des concepts et des défis. La durée estimée est de 3 à 5 heures, avec des solutions à soumettre par courriel avant une réunion en personne. Moov AI, une société de conseil, adapte ses technologies aux clients et encourage l'utilisation d'outils au choix. La revue du test prendra en compte plusieurs aspects, notamment la conception du pipeline de données et du stockage (fiabilité, performance, évolutivité, schéma de données, gestion des erreurs et alertes) ainsi que le système de recommandations (automatisation, connaissance de Git, automatisation des tests et des déploiements).

### Mise en situation

Nous développons une application similaire à Spotify avec notre client. Notre objectif est de personnaliser les listes de lecture pour chaque utilisateur en se basant sur leurs écoutes passées. Nous avons créé un modèle de recommandation et utilisé des données extraites manuellement pour son prototypage. Pour la prochaine phase, nous automatiserons l'ingestion de données à partir de l'API de l'application, comprenant trois endpoints: les chansons disponibles, les utilisateurs et leur historique d'écoute. Un flux de données quotidien sera mis en place pour récupérer automatiquement ces données et les stocker dans une base dédiée au système de recommandation.

1. Élaborer un flux de données, en **python**, conçu pour récupérer quotidiennement les données de l'API.
_Pour lancer le serveur, exécuter la commande `make start` dans votre terminal à la racine du projet._

2. Détailler le schéma de la base de données que vous utiliseriez pour stocker les informations récupérées des trois sources de données mentionnées plus tôt. Quel système de base de données recommanderiez-vous pour répondre à ces besoins et pourquoi?

3. Le client exprime le besoin de suivre la santé du pipeline de données dans son exécution quotidienne. Expliquez votre méthode de surveillance à ce sujet et les métriques clés.

Félicitations, à ce stade les données sont ingérées quotidiennement grâce à votre pipeline de données! Les scientifiques de données sollicitent votre collaboration pour la mise en place de l’architecture du système de recommandation. Votre expertise est sollicitée pour automatiser le calcul des recommandations et pour automatiser le réentrainement du modèle.

5. Dessinez et/ou expliquez comment vous procèderiez pour automatiser le calcul des recommandations.

6. Dessinez et/ou expliquez comment vous procèderiez pour automatiser le réentrainement du modèle de recommandation.

### TODO

Representer les données aussi ici ??

### Trucs et astuces

- Nous estimons la durée de ce test entre 3 et 5 heures suivant votre appétence technique.
- Nous ne privilégions aucune approche spécifique pour vos travaux. Notre intérêt se porte sur les choix que vous effectuez, leur justification, ainsi que sur votre méthodologie de développement.
- Nous vous encourageons à évaluer le degré de normalisation requis pour votre schéma et à déterminer la pertinence de l'utilisation de clés étrangères pour la jointure des tables.
- Il est impératif que votre code soit exécutable.
- Veuillez prendre en considération le type de gestion des erreurs et de tests approprié à votre solution.

## FAQ

### Comment accéder aux données de l'API?

[FastAPI](https://fastapi.tiangolo.com/) est un framework web Python moderne et performant pour la création rapide d'APIs RESTful, offrant une syntaxe intuitive et une documentation interactive automatique. Ce framework est utilisé pour exécuter localement une application.
À la racine du projet, vous pouvez exécuter l'instruction `make start`.

À défaut, vous pouvez vous rendre au niveau de `src/moovitamix_fastapi`, puis exécuter dans votre terminal l'instrcution suivante `python3 -m uvicorn main:app --reload`. Vous retrouverz ensuite l'URL pour accéder à l'application en local. Le chemin /docs doit être ajouté pour accéder à la page de documentation: <http://127.0.0.1:8000/docs>.

---

### TODO: Entretien collaboratif

- Durée : 60 à 90 minutes
- Exploration approfondie des concepts d'ingénierie des données.

Examples:

1. Évaluation des compétences SQL Server (utilisation de RANK, COALESCE, INTERSECT, JOIN - niveau avancé) en exécutant une instance Docker. Proposition d'amélioration de l'image Docker (par exemple, transition vers SQLite).
   - À faire : Utiliser Docker (suggérer l'utilisation de pgAdmin pour interagir avec la base de données)

2. Demander au candidat d'évaluer une Pull Request (durée estimée : 15 minutes chacune).
   - Déploiement d'une infrastructure avec Terraform sur notre environnement.
   - Utilisation de Python.
   - Utilisation de Docker.
   - Compétences en SQL.

- TODO: Prévenir le candidat sur le travail collaboratif: interagir avec une API, faire une revu de code

3. Questions SQLServer (RANK, COALESCE, INTERSECT, JOIN (un peu trop avancé)) à réaliser en exécutant une image Docker (Suggérer une amélioration de l'image (i.e. SQLlite)).

- TODO: Docker (pgAdmin? pour interaction avec la base)

4. Demander au candidat d'évaluer une Pull Request (15m chaque?)
                        -> Déployer une infra avec terraform sur notre infra
                        -> Python
                        -> Docker
                        -> SQL
