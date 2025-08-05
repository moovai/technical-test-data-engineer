# Réponses du test technique

## Étapes 1 à 3 : Documentation technique

### 1. Création de l’environnement virtuel

```bash
python -m venv env
.\env\Scripts\activate

pip install -r requirements.txt
```

### 2. Lancement de l’API et élaboration du pipeline de données

#### Lancement de l’API

Pour démarrer le serveur FastAPI :

```bash
cd src
python -m uvicorn moovitamix_fastapi.main:app --reload
```

Une fois lancé, l’interface Swagger est accessible à l’adresse : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



#### Structure du projet

J’ai structuré le projet autour d’un découpage modulaire pour faciliter la maintenance et les tests :
- `src/moovitamix_fastapi/` : contient entre autres l’application FastAPI et le script principale du pipeline de données.
- `src/moovitamix_fastapi/api/` : contient le client pour récupérer les données depuis les API externes.
- `src/moovitamix_fastapi/utils/` : contient l’écriture des fichiers ou la création des répertoires.
- `test/` : regroupe tous les tests unitaires.

Le fichier principal du flux de données est `run_fetch.py`, situé à la racine du dossier `src/moovitamix_fastapi/`. Ce script constitue le point d’entrée du pipeline. Il orchestre les appels aux trois endpoints de l'API (`/tracks`, `/users`, `/listen_history`) via les fonctions du module `api/`, puis structure et sauvegarde les données extraites.

Les données récupérées sont ensuite  enregistrées localement dans le dossier `data/` sous les fichiers `tracks.json`, `users.json`, et `listen_history.json`, facilitant leur réutilisation sans dépendance à l'API pendant le développement.

#### Tester le flux de données manuellement

Pour exécuter manuellement le pipeline de collecte de données :
```bash
cd src
python -m moovitamix_fastapi.run_fetch
```
Les fichiers JSON sont ensuite disponibles dans le dossier `data/`.

### 3. Tests unitaires 

 **Test de récupération des données via l’API client (`api_client.py`)**  
 Vérifie que le client appelle correctement les endpoints, gère la pagination et renvoie des données au format attendu. 
 
test_fetch_data_success : vérifie que les données sont correctement récupérées d’un endpoint.
test_fetch_data_invalid_endpoint : vérifie que les erreurs (ex : 404) sont bien levées et capturées.  
  

 **Test de la fonction d’écriture des fichiers JSON (`file_writer.py`)**  
  Contrôle que les données extraites sont correctement sauvegardées dans le dossier `data/` sous le bon format et chemin. 

test_save_data_to_json_creates_file : vérifie que le fichier est créé, et que les données sont bien enregistrées.
  
 **Test des routes FastAPI (`main.py`)**  
   test_get_tracks, test_get_users, test_get_listen_history : vérifient que les endpoints exposés renvoient bien une réponse 200 et contiennent une clé "items" avec une liste.
  
 **Test de gestion d’erreurs**  
Implémentation correspondante : test/test_run_fetch.py

  Simulation d’erreurs réseau et de données invalides dans les appels API pour vérifier que le pipeline gère correctement ces cas sans planter.  
  
  test_fetch_and_save_all : exécute la fonction centrale fetch_and_save_all, simule les appels API, et vérifie que les 3 fichiers (tracks.json, users.json, listen_history.json) sont bien générés dans un répertoire temporaire.

-  Remarque  

Des fixtures ont été utilisées pour gérer la création et la suppression de répertoires temporaires lors des tests


#### Exécution des tests

Depuis la racine du projet (là où se trouve le dossier `test/`), exécuter simplement la commande :

```bash
pytest
```
---

## Étapes 4 à 7 : Questions

### Étape 4 : Schéma de la base de données recommandé

#### Tables proposées :

| Table            | Clé primaire | Clés étrangères       |
| ---------------- | ------------ | --------------------- |
| `tracks`         | `id_track`   |                       |
| `users`          | `id_user`    |                       |
| `listen_history` | `id_listen`  | `id_user`, `id_track` |

### 4. Schéma de base de données et recommandation

#### Schéma relationnel proposé

Pour structurer les données récupérées depuis les API `/tracks`, `/users`, et `/listen_history`, j’ai conçu un schéma relationnel normalisé, simple mais extensible :

#### Table : users

| Colonne        | Type        | Contraintes                   |
|----------------|-------------|-------------------------------|
| id             | INTEGER     | PRIMARY KEY                  |
| first_name     | TEXT        | NOT NULL                     |
| last_name      | TEXT        | NOT NULL                     |
| email          | TEXT        | UNIQUE, NOT NULL             |
| gender         | TEXT        | CHECK (gender IN ('Male', 'Female', 'Other')) |
| favorite_genres| TEXT        | NULLABLE (champ CSV ou JSON) |
| created_at     | TIMESTAMP   | NOT NULL                     |
| updated_at     | TIMESTAMP   | NOT NULL                     |

#### Table : tracks

| Colonne        | Type        | Contraintes                   |
|----------------|-------------|-------------------------------|
| id             | INTEGER     | PRIMARY KEY                  |
| name           | TEXT        | NOT NULL                     |
| artist         | TEXT        | NOT NULL                     |
| songwriters    | TEXT        | NULLABLE                     |
| duration       | TEXT        | NOT NULL                     |
| genres         | TEXT        | NULLABLE (champ CSV ou JSON) |
| album          | TEXT        | NULLABLE                     |
| created_at     | TIMESTAMP   | NOT NULL                     |
| updated_at     | TIMESTAMP   | NOT NULL                     |

#### Table : listen_history

| Colonne        | Type        | Contraintes                                       |
|----------------|-------------|---------------------------------------------------|
| id             | INTEGER     | PRIMARY KEY AUTOINCREMENT                        |
| user_id        | INTEGER     | FOREIGN KEY → users(id) ON DELETE CASCADE        |
| track_id       | INTEGER     | FOREIGN KEY → tracks(id) ON DELETE CASCADE       |
| listened_at    | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP                        |

#### Remarques :

- L’API `/listen_history` retourne des paires `{user_id, items}` avec une liste d’`id` de morceaux écoutés. Ces données sont normalisées dans la table `listen_history` avec une ligne par écoute.
- La table `listen_history` peut être enrichie par la suite avec des métadonnées (durée d’écoute, device utilisé, etc.)

#### Recommandation de système de base de données

Pour un environnement réel avec montée en charge, je recommanderais :

- **PostgreSQL** :
  - Puissant support SQL + JSON.
  - Indexation avancée, support de la recherche full-text.
  - Fiabilité et scalabilité.

> Remarque : les types et contraintes sont déduits des réponses JSON observées via Swagger.

---

### Étape 5 : Monitoring de la santé du pipeline de données


**1. Journalisation (logging structuré)**  
Chaque étape du pipeline (`fetch`, `save`) génère des logs horodatés avec :
- Début / fin d’exécution
- Statut de l’appel API
- Nombre d’items récupérés
- Chemin des fichiers générés

*Exemple :*  
`[2025-08-04 08:00:01] INFO - Fetched 100 items from /tracks, saved to data/tracks.json`

**2. Validation automatique du résultat**

Après chaque exécution, une vérification de l’intégrité est effectuée :
- Présence des fichiers `tracks.json`, `users.json`, `listen_history.json`
- Taille minimale des fichiers
- Conformité structurelle de base (clés attendues)

> En cas d’échec : log d’erreur, possibilité d’alerte mail a travers un serveur SMTP.

**3. Statistiques quotidiennes**

Un fichier `data/pipeline_stats.csv` peut stocker des résumés :

| date       | endpoint        | items_fetched | duration_sec | status  |
|------------|------------------|----------------|--------------|---------|
| 2025-08-04 | /tracks          | 105            | 1.45         | success |
| 2025-08-04 | /users           | 50             | 0.87         | success |
| 2025-08-04 | /listen_history  | 140            | 1.02         | success |


####  Métriques clés à surveiller

| **Métrique**                  | **Description** |
|---------------------------|-------------|
|  Volume extrait      | Nombre d’items par endpoint |
|  Statut HTTP         | Codes 200 / erreurs API |
|  Temps d’exécution   | Durée des appels |
|  Intégrité des fichiers | Présence et format JSON valide |
|  Horodatage d’exécution | Confirmation d’une exécution quotidienne |

---

### Étape 6 : Automatisation du calcul des recommandations

####  Méthode de calcul des recommandations

Pour chaque utilisateur, le moteur de recommandation suivra ces etapes

1. **Analyse des écoutes passées** :
   - Regrouper les morceaux écoutés par l'utilisateur (`listen_history`)
   - Extraire les genres, artistes et albums les plus fréquents
   - Pondérer selon la fréquence d’écoute (plus un genre/artiste est écouté, plus il est pertinent)

2. **Croisement avec les préférences déclarées** :
   - Extraire le champ `favorite_genres` depuis `users.json`
   - Attribuer un poids fixe à ces genres déclarés, même s'ils ne ressortent pas de l’historique

3. **Filtrage de l’univers musical** :
   - Éliminer les titres déjà écoutés (éviter redondance)
   - Identifier les morceaux similaires selon :
      **Genre**
      **Artiste**
      **Album**

4. **Scoring final et sélection** :
   - Pour chaque morceau candidat non encore écouté :
     ```python
     score = 0
     if genre in genres_écoutés: score += 2
     if genre in favorite_genres: score += 1.5
     if artiste in artistes_écoutés: score += 1.5
     if album in albums_écoutés: score += 1
     ```
   - Trier par score décroissant et conserver les **10 meilleurs morceaux**

---

### Étape 7 : Automatisation du réentrainement du modèle

#### Fréquence suggérée :

- Par défaut : quotidienne

Possibilité de passer à hebdomadaire si les données évoluent lentement et  selon le comportement utilisateur

#### Pipeline type :

1. Extraction des nouvelles données (utilisateurs + écoutes)
2. Préparation des données : 
Agrégation des statistiques d’écoute
Nettoyage et formatage des données d’entrée
3. Recalcul des recommandations :
Relance du script de scoring
Génération des top 10 pour chaque utilisateur
4. Stockage & historisation:
Écriture dans un fichier versionné ou table SQL (timestamp, user_id, recommendations)

#### Orchestration :

- Option simple : tâche planifiée (cron, schedule)

- Option avancée : orchestrateur type Airflow,

#### Remarques :

Le moteur de recommandation actuel repose sur un système de scoring pondéré basé sur les comportements d'écoute et préférences. Son réentraînement consiste à recalculer les scores à partir des données mises à jour chaque semaine, via un script orchestré automatiquement.