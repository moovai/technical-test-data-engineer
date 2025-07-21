# Réponses du test

Question 1 : fichier **src/data_pipeline.py**
```python
import requests
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "data"

ENDPOINTS = ["tracks", "users", "listen_history"]

def fetch_data(endpoint: str, page: int = 1, size: int = 100):
    url = f"{BASE_URL}/{endpoint}?page={page}&size={size}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def save_data(data, filename: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)

def run_pipeline():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for endpoint in ENDPOINTS:
        data = fetch_data(endpoint)
        if data is not None:
            save_data(data, f"{endpoint}_{timestamp}.json")

if __name__ == "__main__":
    run_pipeline()
```

Question 3 : fichier **test/tests_pipeline.py**
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import json
import os
from unittest.mock import patch, Mock
from moovitamix_fastapi.data_pipeline import fetch_data, save_data
from requests.exceptions import RequestException

def test_fetch_data_success():
    mock_response = {"data": "example"}

    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_response

        result = fetch_data("tracks")
        assert result == mock_response
        mock_get.assert_called_once()

def test_fetch_data_failure():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = RequestException("API down")

        result = fetch_data("tracks")
        assert result is None

def test_save_data(tmp_path):
    data = {"test": 123}
    filename = "test_file.json"
    file_path = tmp_path / filename

    save_data(data, file_path)

    with open(file_path) as f:
        loaded = json.load(f)
        assert loaded == data
```

## _Utilisation de la solution (étape 1 à 3)_

1. Utilisation du pipeline de données
```shell
python src/moovitamix_fastapi/data_pipeline.py
```

2. Test du pipeline de données
```shell
pytest test/tests_pipeline.py
```

3. Lancement du pipeline de données une fois par jour
* Ouvrir l'éditeur de crontab
```shell
crontab -e
```
* Ajouter un job journalier
```shell
0 2 * * * /usr/bin/python3 ~/src/moovitamix_fastapi/data_pipeline.py >> ~/logs/logfile.log 2>&1
```

## Questions (étapes 4 à 7)

### Étape 4

Schéma pour une base de données PostgreSQL
```SQL
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    gender          TEXT CHECK (gender IN (
                        'Male', 'Female', 'Non-binary', 'Genderqueer', 'Genderfluid',
                        'Agender', 'Bigender', 'Gender questioning', 'Gender nonconforming'
                    )),
    favorite_genres TEXT,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

CREATE TABLE tracks (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    artist          TEXT NOT NULL,
    songwriters     TEXT,
    duration        INTERVAL,
    genres          TEXT,
    album           TEXT,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

CREATE TABLE listen_history (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    track_id        INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    listened_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

J'ai choisi un base de données relationnelle plutôt que de type NoSQL parce qu'il y a une relation claire entre les utilisateurs, les morceaux et l'historique des écoutes. Ce schéma permet de facilement extraire, par exemple, le top 10 des morceaux écoutés grâce à SQL.
Une base NoSQL comme MongoDB ou DynamoDB aurait comme avantage de scaler horizontalement plus facilement et d'écrire à une plus haute fréquence, mais forcerait les requêtes plus complexes (avec JOIN, GROUP BY, ORDER BY, ...) à être exécutées côté client et obligerait à lire plus de données que nécessaire.
Parmi les BDD relationnelles, PostgreSQL a quelques avantages comme des types modernes (JSONB, ARRAY, custom, ...) ou le côté open source et gratuit.

### Étape 5

Pour s'assurer de la bonne santé du pipeline, voici les métriques que je mesurerai:

* Nombre total de succès et d'échecs quotidiens, pour détecter un changement soudain
* Taux de succès par endpoint, pour s'assurer que chaque endpoint fonctionne correctement
  ```
  Nombre d'endpoints en erreur / total d'endpoints
  ```
* Temps d'exécution du pipeline, pour détecter un changement soudain
  ```
  Date de fin - date de début du pipeline
  ```
* Taille des données extraites, pour détecter un volume anormal (nul ou trop important)
  ```
  Volume de données récupérées par endpoint
  ```

Ces métriques pourraient être analysées à partir des logs quotidiennes. Elles pourraient être remontées par email avec un script exécuté par cron, ou par un outil comme Prometheus visualisé avec Grafana.

### Étape 6

Je créerai une table PostgreSQL pour enregistrer les recommandations
```sql
CREATE TABLE user_recommendations (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendations INTEGER[] NOT NULL, -- tableau de track_id
    calculated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
````

Ensuite, comme pour le script data_pipeline.py, j'utiliserai cron pour exécuter le script de calcul des recommandations et je stockerai le résultat dans cette table. Cette exécution devrait se faire après celle du pipeline.


### Étape 7

Pour réentrainer le modèle automatiquement, je mettrais en place un pipeline hebdomadaire avec les étapes suivantes:
* Vérification que les conditions sont réunies (par exemple suffisamment de nouvelles données ou un certain temps s'est écoulé depuis la dernière exécution)
* Préparation des données (extraction, agrégations, ...)
* Exécution du script de réentrainement
* Validation du nouveau modèle. S'il n'est pas validé, envoi d'une alerte aux scientifiques de données.
* Déploiement en production