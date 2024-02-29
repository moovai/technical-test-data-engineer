## Objectif

Ce test est élaboré pour mettre en lumière votre expertise dans le domaine de l'ingénierie des données à travers l'utilisation du langage de programmation Python. Il vise également à évaluer votre capacité à soutenir les scientifiques des données dans le développement de solutions d'intelligence artificielle.

Le test se déroule en deux étapes:

1. Test technique: compléter les différentes sections de ce test décrites ci-dessous avant votre entretien.
2. Entretien collaboratif: présentation de vos réalisations lors de notre rencontre.

La phase de travail collaboratif a pour objectif de nous donner un aperçu de ce à quoi il serait de travailler ensemble et devrait être perçue comme un effort mutuelle. S'en terminera un échange d'expériences sur le test dans son ensemble.

## Prérequis

- Connaissance d'outils d'orchestration (e.g. Airlfow).
- Connaissance des APIs et de leurs protocoles.
- Connaissance des bases de données relationnelles.
- Connaissance avancées de Python dans les domaines suivants: analyse, visualisation de données et tâches de script.
- Familiarité avec Docker. Vous aurez besoin de Docker installé sur votre machine de développement.
- Familiarité avec Git pour le contrôle de source. Un compte [github.com](github.com) est suggéré pour partager votre code.
- Fondamentaux des commandes SQL (DDL, DML).

Veuillez noter que ce test technique ne nécessite *aucun frais* de votre part.

## Contexte

TODO: Ajouter une partie de l'énoncé raccourci du test inital + demander explicitement de batir partiellement l'ETL avec Python
TODO: Fournir du matérial de support pour le test (e.g. lancer FastAPI en local)
TODO: SQL Server en local pour effectuer des requêtes

## Problèmes

### Test technique

TODO: Ce test doit être léger et précis sur le travail attendu

La séquence d'étapes suivantes est à compléter. Nous estimons la durée de ce test entre 3 et 5 heures suivant votre appétence technique.

Test technique (le rendre le plus léger)

1. Suggérer de faire un Fork de de ce dépôt git votre compte personnel GitHub.
2. APIs (à déployer localement)
    Travail attendu
        - Collecte, schéma de données pour le stockage, traitement,
    Presentation
        - comment l'intégrer dans une solution cloud, santé pipeline, Automatisation calcul de recommandation, ré-entrainement du modèle
        - Notebook, Git, Test, DevOps

### Entretien collaboratif

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

3. Questions SQLServer (RANK, COALESCE, INTERSECT, JOIN (un peu trop avancé)) à réaliser en executant une image Docker (Suggérer une amélioration de l'image (i.e. SQLlite)).
- TODO: Docker (pgAdmin? pour interaction avec la base)

4. Demander au candidat d'évaluer une Pull Request (15m chaque?)
                        -> Déployer une infra avec terraform sur notre infra
                        -> Python
                        -> Docker
                        -> SQL

### Trucs et conseils

- Nous ne privilégions aucune approche particulière pour cette tâche. Notre intérêt se porte sur les choix que vous effectuez, la justification de ces choix, ainsi que sur votre méthodologie de développement.
- Nous vous encourageons à évaluer le degré de normalisation requis pour votre schéma et à déterminer la pertinence de l'utilisation de clés étrangères pour la jointure des tables.
- Il est impératif que votre code soit exécutable.
- Veuillez prendre en considération le type de gestion des erreurs et de tests approprié à votre solution.
