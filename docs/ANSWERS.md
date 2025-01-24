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

_votre réponse ici_

### Étape 5

_votre réponse ici_

### Étape 6

_votre réponse ici_

### Étape 7

_votre réponse ici_
