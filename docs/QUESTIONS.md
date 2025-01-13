# Objectif

Ce test est élaboré pour mettre en lumière votre expertise dans le domaine de l'ingénierie des données à travers l'utilisation du langage de programmation Python. Il vise également à évaluer votre capacité à soutenir les scientifiques des données dans le développement de solutions d'intelligence artificielle.

Le test se déroule en deux volets:

1. Test technique: compléter les différentes sections de ce test décrites ci-dessous avant votre entretien.
2. Entretien collaboratif: présentation de vos réalisations lors de notre rencontre.

La phase de travail collaboratif a pour objectif de nous donner un aperçu de ce à quoi il serait de travailler ensemble et devrait être perçue comme un effort mutuel. S'en terminera un échange d'expériences sur le test dans son ensemble.

# Prérequis

- Connaissance des outils d'orchestration.
- Connaissance des APIs et de leurs protocoles.
- Connaissance des systèmes de bases de données.
- Connaissance avancée de Python dans les domaines suivants: analyse, visualisation de données et tâches de script.

Veuillez noter que ce test technique ne nécessite *aucun frais* de votre part.

## Contexte

Le test technique évalue des aspects clés de l'ingénierie de données chez Moov AI : la conception et la mise en œuvre de flux de données pour alimenter des modèles, ainsi que le soutien aux scientifiques de données dans la mise en place de solutions de machine learning. Il ne se concentre pas sur les compétences spécifiques des outils, mais sur la compréhension des concepts et des défis. La durée estimée est de 3 à 5 heures, avec des solutions à soumettre par courriel avant une réunion en personne. Moov AI, une société de conseil, adapte ses technologies aux clients et encourage l'utilisation d'outils au choix. La revue du test prendra en compte plusieurs aspects, notamment la conception du pipeline de données et du stockage (fiabilité, performance, évolutivité, schéma de données, gestions des erreurs et alertes) ainsi que le système de recommandations (automatisation, connaissance de Git, automatisation des tests et des déploiements).

### Mise en situation

Nous développons une application similaire à Spotify avec notre client. Notre objectif est de personnaliser les listes de lecture pour chaque utilisateur en se basant sur leurs écoutes passées. Nous avons créé un modèle de recommandation et utilisé des données extraites manuellement pour son prototypage. Pour la prochaine phase, nous automatiserons l'ingestion de données à partir de l'API de l'application, comprenant trois endpoints: les chansons disponibles, les utilisateurs et leur historique d'écoute. Un flux de données quotidien sera mis en place pour récupérer automatiquement ces données et les stocker dans une base dédiée au système de recommandation.

---

**Important:**

- [Forker le dépôt](https://github.com/moovai/technical-test-data-engineer/fork), puis soumettez une pull request en contribuant sur la branche `develop` pour envoyer vos travaux.
- Un fichier `docs/ANSWERS.md` est fourni pour :  
  - guider l'utilisateur dans l'utilisation de votre solution (étapes 1 à 3).  
  - répondre aux questions (étapes 4 à 7).
- Limiter votre travail de programmation uniquement aux **étapes 1 à 3** incluses.

---

1. Un fichier `requirements.txt` liste les librairies à utiliser pour l'étape 2. Créer un environnement virtuel avec l'outil de votre choix et activez-le.

2. Élaborer un flux de données, en **python**, conçu pour récupérer quotidiennement les données de l'API.
*Pour lancer le serveur, déplacez-vous dans le dossier `src/moovitamix_fastapi` puis exécuter la commande `python -m uvicorn main:app`.*

3. Mettez en place quelques tests unitaires sur les composants de votre flux de données.
*Choisissez judicieusement des tests unitaires essentiels pour votre flux de données, sans exagérer leur nombre.*

4. Détailler le schéma de la base de données que vous utiliseriez pour stocker les informations récupérées des trois sources de données mentionnées plus tôt. Quel système de base de données recommanderiez-vous pour répondre à ces besoins et pourquoi?

5. Le client exprime le besoin de suivre la santé du pipeline de données dans son exécution quotidienne. Expliquez votre méthode de surveillance à ce sujet et les métriques clés.

   Félicitations, à ce stade les données sont ingérées quotidiennement grâce à votre pipeline de données! Les scientifiques de données sollicitent votre collaboration pour la mise en place de l’architecture du système de recommandation. Votre expertise est sollicitée pour automatiser le calcul des recommandations et pour automatiser le réentrainement du modèle.

6. Dessinez et/ou expliquez comment vous procèderiez pour automatiser le calcul des recommandations.

7. Dessinez et/ou expliquez comment vous procèderiez pour automatiser le réentrainement du modèle de recommandation.

### Trucs et astuces

- Nous estimons la durée de ce test entre 3 et 5 heures suivant votre appétence technique.
- Le projet a été testé avec python "^3.9,<3.13", nous vous recommandoncs une version comprise dans cette plage.
- Nous ne privilégions aucune approche spécifique pour vos travaux. Notre intérêt se porte sur les choix que vous effectuez, leur justification, ainsi que sur votre méthodologie de développement.
- Nous vous encourageons à évaluer le degré de normalisation requis pour votre schéma et à déterminer la pertinence de l'utilisation de clés étrangères pour la jointure des tables.
- Il est impératif que votre code soit exécutable.
- Veuillez mettre en place la gestion des erreurs et test approprié à votre solution.
- Vous avez la possibilité d'enregistrer les données localement; une base de données n'est pas nécessaire pour ce test.

## FAQ

### Comment accéder aux données de l'API?

[FastAPI](https://fastapi.tiangolo.com/) est un framework web Python moderne et performant pour la création rapide d'APIs RESTful, offrant une syntaxe intuitive et une documentation interactive automatique. Ce framework est utilisé pour exécuter localement une application.

Placez vous dans le dossier `src/moovitamix_fastapi`, puis exécuter dans votre terminal l'instruction suivante `python -m uvicorn main:app --reload`. Vous retrouverz ensuite l'URL pour accéder à l'application en local. L'application vous redirige automatiquement vers le chemin /docs, si ce n'est pas le cas, rendez-vous directement à: <http://127.0.0.1:8000/docs>.

### Comment rendre mes travaux ?

Vos travaux sont attendus sous forme de pull request sur notre [dépôt](https://github.com/moovai/technical-test-data-engineer/). Aidez-vous de la documention officiel de [github](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) pour trouvez les bonnes ressources à ce sujet.

### Comment rouler les tests ?

[PyTest](https://docs.pytest.org/en/8.2.x/) est un framework de test pour Python. Il permet de créer des tests unitaires, d'intégration et de fonctionnalité de manière simple et efficace. Pytest facilite l'écriture des tests en utilisant une syntaxe claire et concise.

Pour exécuter les tests, diriger vous à la racine du projet et exécuter la commande `pytest`.
Le résultat devrait ressemblait à ceci:

```bash
=================================================================================== test session starts ===================================================================================
platform darwin -- Python 3.9.19, pytest-8.2.1, pluggy-1.5.0
rootdir: /Users/noesautel/Git/technical-test-data-engineer
plugins: Faker-25.3.0, anyio-4.4.0
collected 3 items                                                                                                                                                                         

test/test_classes_out.py ...                                                                                                                                                        [100%]

==================================================================================== 3 passed in 0.12s ====================================================================================
```
