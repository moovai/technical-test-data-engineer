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
python -m uvicorn main:app
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

## 4. Tests untaires (Pytest)

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

Il y a trois "layers" au schéma proposé:

A - Raw Layer
Dans ce niveau, chaque table contient quatre colonnes principales : **ID, UPDATED_AT, INGESTED_AT, PAYLOAD**.  
Le champ `payload` stocke l’objet JSON brut provenant de l’API.  

```bash
CREATE TABLE raw_tracks (
  id           BIGINT PRIMARY KEY,
  updated_at   TIMESTAMPTZ,
  ingested_at  TIMESTAMPTZ,
  payload      JSONB NOT NULL
);
```

Pourquoi conserver le payload en JSON ?

1. Évolution du schéma : les APIs changent souvent (ajout/suppression/renommage de champs). Stocker le brut protège contre les breaking changes.

2. Flexibilité : chaque équipe (ML, Analytics, Ops) peut créer ses propres vues transformées à partir de la donnée brute.


B - Intermediate layer (Normalization)

Ici, on normalise les données du Raw Layer en tables dimensionnelles et factuelles.

- Les clés du JSON deviennent des colonnes.
- Les valeurs deviennent des lignes.
- Pour la table listen_history, le tableau items est explosé : chaque écoute devient une ligne unique.
- On ajoute une colonne listen_order pour garantir une clé unique (car un utilisateur peut écouter plusieurs fois la même chanson).

```bash
CREATE TABLE fact_listens (
  user_id       BIGINT NOT NULL REFERENCES dim_users(user_id),
  track_id      BIGINT NOT NULL REFERENCES dim_tracks(track_id),
  listen_order  INT    NOT NULL,               -- position 1..N dans l’historique de l’utilisateur
  updated_at    TIMESTAMPTZ,                   
  PRIMARY KEY (user_id, listen_order)
);

CREATE TABLE dim_users (
  user_id        BIGINT PRIMARY KEY,
  first_name     TEXT,
  last_name      TEXT,
  email          TEXT,
  gender         TEXT,
  favorite_genres TEXT,
  created_at     TIMESTAMPTZ,
  updated_at     TIMESTAMPTZ
);

CREATE TABLE dim_tracks (
  track_id    BIGINT PRIMARY KEY,
  name        TEXT NOT NULL,
  artist      TEXT NOT NULL,
  songwriters TEXT,
  duration    TEXT,
  genres      TEXT,
  album       TEXT,
  created_at  TIMESTAMPTZ,
  updated_at  TIMESTAMPTZ
);
```

C - ML ready table (Ce que le modèle pourrait utilisé)

Une table dénormalisée qui rassemble les informations essentielles pour l’entraînement d’un modèle de recommandation :

| user_id | user_name | track_id | track_name | genre | artist  | album   | listen_order | 
|---------|-----------|----------|------------|-------|---------|---------|--------------|
| 17081   | Alice     | 87643    | Song A     | Rock  | Band X  | Album 1 | 1            |
| 17081   | Alice     | 27349    | Song B     | Pop   | Artist Y| Album 2 | 2            |
| 17081   | Alice     | 41878    | Song C     | Jazz  | Artist Z| Album 3 | 3            |

####Choix du système de base de données

- Court terme : commencer avec PostgreSQL tant que les tables restent sous ~10M de lignes.

   -  Simple d’utilisation.
   - Supporte bien les PK/FK.
   - Permet de stocker les payloads bruts en JSON.

- Long terme (100M+ lignes) : PostgreSQL devient limité.

   - Stockage row-based → peu optimal pour de gros scans analytiques.
   - Parallélisation limitée → pas de MPP natif comme Snowflake, BigQuery ou Redshift.
   - Scalabilité verticale → tu rajoutes RAM/CPU, mais ça plafonne rapidement.

Pour passer à l’échelle, je recommande un data warehouse distribué comme Snowflake ou Databricks (scalabilité horizontale, MPP, optimisé pour le big data, column-based).

### Étape 5

## Suivi de la santé du pipeline de données

Pour garantir la fiabilité des données ingérées quotidiennement, je mettrais en place un **système de monitoring du pipeline**, basé sur les points suivants :

### Méthode de surveillance
- **Orchestration** : utilisation d’un orchestrateur (ex. Airflow) avec des logs détaillés pour chaque tâche (ingestion, transformation, stockage).  
- **Alertes automatisées** : configuration d’alertes (ex. Slack, email) si une tâche échoue, dépasse un temps d’exécution défini, ou charge un volume anormalement faible/élevé de données.  
- **Historisation des runs** : conserver un registre (table de métadonnées) avec le statut de chaque exécution du pipeline (succès, échec, durée, volume de données).  
- **Data quality checks** : mise en place de tests automatisés (ex. Great Expectations, dbt tests) pour s’assurer que les données sont complètes et valides.  

### Métriques clés
- **Disponibilité et statut des tâches**
  - % de succès/échec par exécution.  
  - Temps d’exécution moyen vs attendu.  

- **Volumes de données ingérées**
  - Nombre de chansons, utilisateurs et écoutes ingérés chaque jour.  
  - Comparaison avec les jours précédents (détection d’anomalies).  

- **Qualité des données**
  - Champs obligatoires non nuls (ex. `id`, `user_id`, `track_id`).  
  - Respect des formats (ex. timestamp valide pour `updated_at`).  
  - Détection de doublons.  

- **Fraîcheur des données**
  - Vérifier que les données du jour J-1 sont bien arrivées.  
  - Mesurer le décalage entre l’heure d’ingestion et la dernière mise à jour (*lag*).

### Étape 6

## Automatisation du calcul des recommandations

### Étapes principales
1. **Ingestion quotidienne** : récupérer les données (users, tracks, historique) via l’API et les stocker.  
2. **Préparation des données** : nettoyer, normaliser et construire des tables prêtes pour le ML (écoutes, profils utilisateurs, infos des morceaux).  
3. **Génération des candidats** : pour chaque utilisateur, sélectionner un ensemble de morceaux potentiellement intéressants (basé sur similarité ou popularité).  
4. **Ranking** : appliquer un modèle (ex. LightGBM ou ALS) qui score les candidats et produit le Top-N morceaux par utilisateur.  
5. **Publication** : stocker les recommandations dans une table `reco_batch(user_id, track_id, score, generated_at)` et les exposer à l’application (ou via un cache type Redis).  

### Orchestration & Monitoring
- Utiliser un orchestrateur (Airflow) qui exécute ces étapes chaque nuit.  
- Surveiller : succès/échec, volumes ingérés, fraîcheur des données.  
- Déclencher des alertes si une étape échoue ou si le volume est anormal.  

### Étape 7

#### Idée générale
À chaque arrivée de nouvelles données (écoutes, utilisateurs, morceaux), un **pipeline automatisé** :
1. Prépare les données,  
2. Ré-entraîne le modèle,  
3. Valide les performances,  
4. Déploie le modèle si les résultats sont satisfaisants.  

---

#### Étapes

1. **Déclenchement**
   - Tous les jours (cron/Airflow) ou après ingestion complète des données.

2. **Préparation des données**
   - Lecture des tables (`users`, `tracks`, `listen_history`).  
   - Filtrage de la période utile (ex. 90 derniers jours).  
   - Construction des features.  
   - Sauvegarde du dataset d’entraînement versionné (ex. `training/2025-08-17.parquet`).

3. **Entraînement**
   - Lancer un script (`train.py`).  
   - Produire un modèle **candidat** + métriques.

4. **Validation**
   - Comparer le modèle candidat au modèle **actuel**.  
   - Si meilleur → continuer.  
   - Sinon → garder l’ancien modèle et alerter.

5. **Versioning & déploiement**
   - Sauvegarde du modèle (MLflow ou équivalent).  
   - Mise à jour du modèle en production (`latest`).

6. **Monitoring**
   - Suivi des métriques (succès/échec, temps d’exécution, volume de données).  
   - Alertes (Slack/email) en cas d’anomalie.