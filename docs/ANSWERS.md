# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

# Moovitamix - Ingestion de Données

Ce projet fournit :
- une **API FastAPI** qui génère des données factices (tracks, users, listen_history),
- un flux d’**ingestion incrémentale** (stockage local au format JSON, watermark),
- une **orchestration quotidienne** via **Airflow** (Docker),
- quelques **tests unitaires** essentiels. Ceux-ci seront invokés à chaque push via une GitHub action.

---

## 1. Installation

Créez et activez un environnement virtuel, puis installez les dépendances listées dans `requirements.txt`.

```bash
# Créer un environnement virtuel (exemple avec venv)
python -m venv .venv
source .venv/bin/activate   # Sur Windows : .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

```
## 2. Lancer le serveur FastAPI

Déplacez-vous dans le dossier de l’application FastAPI et démarrez le serveur :

```bash
cd src/moovitamix_fastapi
python -m uvicorn main:app --reload
```
Le serveur sera disponible à l’adresse : http://127.0.0.1:8000
Documentation Swagger UI : http://127.0.0.1:8000/docs

## 3. Orchestration avec Airflow (Docker)

Prérequis

- Docker & Docker Compose

Démarrage

Depuis la racine du repo (là où se trouve docker-compose.yml) :

```bash
docker compose up --build
```

Cela :

- installe les dépendances Airflow (via requirements-airflow.txt),
- initialise Airflow et lance webserver + scheduler,
- monte le code d’ingestion dans le conteneur.

Accès à l’UI

Airflow UI : http://localhost:8080
(configuré en NoAuth pour simplifier la revue)

Déclencher le DAG

Dans l’UI, active le DAG daily_ingest puis clique Play ▶ Trigger DAG.

Le DAG fait :

- incremental_load_tracks
- incremental_load_users
- incremental_load_listen_history

Où vont les données ?

Les fichiers JSON sont écrits dans ./data_store/ :

tracks.json, users.json, listen_history.json

watermark.json (pour mémoriser le updated_at max par table)

Important (réseau Docker) : dans docker-compose.yml, l’ingestion utilise BASE_URL=http://host.docker.internal:8000 pour atteindre l’API qui tourne sur ta machine. Si tu changes de port ou d’hôte, adapte cette variable d’environnement.

## 4. Exécuter l’ingestion sans Airflow (manuel)

Depuis la racine (avec l’API allumée) :

```bash
python -m data_ingestion.load_data
```

Cela télécharge les pages, applique le watermark et fait des upserts locaux dans data_store/.

## 5. Tests untaires (Pytest)

```bash
pytest -q
```

Les tests couvrent :

- la pagination (iter_pages),
- l’ingestion incrémentale (filtre via watermark + mise à jour du watermark),
- l’upsert local (pas de doublons, remplacement seulement si updated_at plus récent).

## 6. Structure (résumé)

```bash
.
├─ data_ingestion/
│  ├─ fetch_data.py                       # session + pagination
│  └─ load_data.py                        # upsert local + watermark + incremental_load
├─ data_store/                            # Fichiers JSON (créé au runtime)
│ ├─ listen_history.json
│ ├─ tracks.json
│ ├─ users.json
│ └─ watermark.json
├─ orchestrator/
│  ├─ dags/
│  │  └─ daily_ingest.py                  # DAG Airflow (3 tâches d’ingestion)
│  ├─ airflow_home/                       # Config locale Airflow
│  ├─ webserver_config.py
│  └─ requirements-airflow.txt             
├─ src/moovitamix_fastapi/
│  ├─ main.py                             # API FastAPI
│  ├─ classes_out.py
│  └─ generate_fake_data.py
├─ test/                                  # tests pytest
│  ├─ confest.py                          # Fixtures
│  ├─ test_bulk_insert_and_watermark.py   
│  ├─ test_classes_out.py
│  ├─test_incremental_idempotent.py
│  ├─test_incremental_load.py
│  └─ test_iter_pages.py
├─ docker-compose.yml
├─ pytest.ini
├─ requirements.txt
└─ README.md
```

## Questions (étapes 4 à 7)

### Étape 4

_votre réponse ici_

### Étape 5

_votre réponse ici_

### Étape 6

_votre réponse ici_

### Étape 7

_votre réponse ici_
