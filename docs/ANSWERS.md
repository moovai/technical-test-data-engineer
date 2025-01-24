# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

### Étape 1

Creation de l'environnement virtuel, version python supportee entre 3.9 et 3.13. 
```bash
python3.12 -m venv .venv
```
Activation de l'environnement virtuel
```bash
source .venv/bin/activate
```
Installation des dépendances
```bash
pip install -r requirements.txt
```
Pour lancer le serveur
```bash
cd src/moovitamix_fastapi
python -m uvicorn main:app --reload
```
Si le port 8000 est déjà utilisé, ajouter le port 8001 par exemple
```bash
python -m uvicorn main:app --reload --port 8001
```
### Étape 2

Pour lancer le pipeline
```bash
cd src/pipeline_etl
python pipeline.py
```
Le serveur FastAPI doit être lancé avant de lancer le pipeline.

Pour mon Pipeline, j'ai choisi de le developper en une seule classe pour avoir une architecture simple,facilement maintenable et ouvert à l'extension.
J'ai fais un simple github action pour le lancer chaque jour à 00:00 et de push les données dans le repo. C'est sur que en prod reel, j'enverrai les données sur une base de données ou un bucket.

### Étape 3

Pour lancer les tests

```bash
pytest test/test_pipeline.py
```

J'ai fait des tests unitaires pour les fonctions de transformation et de fetch.

## Questions (étapes 4 à 7)

### Étape 4

Pour représenter les données, je vois deux tables avec une table asscociative entre les deux.

- Tracks:
    - track_id: INTEGER PRIMARY KEY
    - name: TEXT
    - artist: TEXT
    - songwriters: TEXT
    - duration: INTEGER
    - genres: TEXT
    - album: TEXT
    - created_at: DATETIME
    - updated_at: DATETIME
- Users:
    - user_id: INTEGER PRIMARY KEY
    - gender: TEXT
    - favorite_genre: TEXT
    - created_at: DATETIME
    - updated_at: DATETIME
- Listen_history:
    - user_id: INTEGER REFERENCES Users(user_id)
    - track_id: INTEGER REFERENCES Tracks(track_id)
    - count: INTEGER
    - created_at: DATETIME
    - updated_at: DATETIME
    - PRIMARY KEY (user_id, track_id)

Pour la table Listen_history, j'ai choisi de faire une table asscociative entre les deux tables pour pouvoir faire des requetes plus facilement, j'ai mis une clef primaire composée de user_id et track_id pour que les données soient uniques et si un utilisateur ecoute plusieurs fois le meme titre, cela sera pris en compte en incrementant la valeur de count.

Concernant le choix de la base de données, la plupart des SGBDR sont applicables. Si je devais choisir pour la simplicité, je choisirais SQLite, tres facile à mettre en place et a configurer. Mais si je devais choisir quelque chose de plus robuste et performant, je choisirais PostgreSQL.

### Étape 5

Pour la surveillance, je choisirais le combo Prometheus + Grafana. Prometheus permet de collecter les données de performance et de mettre en place des alertes. Grafana permet de visualiser les données de performance et de mettre en place des dashboards.

Metriques clefs:
- Taux de succes de la requete fetch
- Taux de succes du pipeline complet
- Temps de traitement du pipeline
- Temps moyen de traitement pour un endpoint (Extract, Transform, Load pour le endpoint)
- Volume moyen des données ingérées (daily, weekly, monthly)
- Indicateur d'augmentation ou reduction de la taille des données ingérées
- Temps de reponses de l'API
- Moyenne CPU durant le traitement

Concernant le client, il est facile de mettre en place un Webhook pour que le client soit notifier en cas d'erreur ou de succes du pipeline sur son application de preference (email, slack, discord, etc...)

### Étape 6

Pour automatiser le calcul des recommendations, apres l'ingestion des donnees du pipeline quotidien, nous pouvons utiliser un job pour lancer une nouveau calcul des recommendations pour les utilisateurs. Dans ce cas on se trouve dans une cas de batch processing donc les users auront des recommendations journalieres

Apres la fin de l'ingestion des donnees, nous pouvons lancer une job pour le calcul des nouvelles recommendations. Ce qui donne des recommandations journalieres pour les utilisateurs. Cela revient a faire un batch processing pour le calcul des recommendations.

Ensuite nous devons sauvegarder les recommendations dans la base de donnees qui est utilisee pour le calcul des recommendations. Et elle seront accessibles par les utilisateurs via une requete API.

Pour la gestion des erreurs, nous pouvons mettre en place un systeme de log qui enregistre les erreurs dans un fichier ou une base de donnees. Et nous pouvons mettre en place un systeme de notification qui envoie un email ou un message a l'equipe en cas d'erreur.



### Étape 7

Pour automatiser le réentraiment du modele de recommandations, nous pouvons mettre en place une nouvelle job qui est executer apres l'ingestions quotidienne des donnees. Cela permet de mettre a jour le modele de recommandations avec les nouvelles donnees.

Donc la job demarre avec le traitement des nouvelles donnees pour le modele, nous devons nettoyer, normaliser et mettre en avant les features les plus pertinantes deja etablie pour le modele de recommandations.

Ensuite nous pouvons utiliser un outil comme MLflow pour le réentraiment du modele de recommandations avec l'ajout de nouvelles données.
MLflow nous permet de suivre le cycle de vie des modeles de recommandations, de les sauvegarder et de les deplacer dans des environnements de production.

Une fois le modele entrainer et evaluer,si le modele est performant, meilleur que le modele precedent et qu'il remplit les conditions d'acceptation, nous pouvons le sauvegarder et le deployer dans un environnement de production.

Nous pouvons mettre en place un systeme de surveillance pour le modele de recommandations. Cela permet de suivre les performances du modele et de detecter les erreurs. Mais aussi de rendre compte via des dashboard de la performance des modeles de recommandations. Mettre aussi en place des alertes sur le drift des donnees pour notifier les scientifiques de donnees en cas de changement de comportement des donnees.