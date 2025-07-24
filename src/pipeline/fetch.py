import requests
import sqlite3
from schedule import  every, repeat, run_pending
import schedule
import time
import logging
#from src/moovitamix_fastapi/classes_out import UserOut, ListenHistoryOut, TracksOut


base_url = "http://localhost:8000"
db_file = 'moovitamix.db'

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

# ---------- Base de données ----------
def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA journal_mode = WAL;
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS tracks (
            id            INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            artist        TEXT NOT NULL,
            songwriters   TEXT,
            duration      INTEGER,
            genres        TEXT,
            album         TEXT,
            created_at    TEXT,
            updated_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY,
            first_name    TEXT NOT NULL,
            last_name     TEXT NOT NULL,
            email         TEXT UNIQUE,
            gender        TEXT,
            favorite_genres TEXT,
            created_at    TEXT,
            updated_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS listen_history (
            user_id    INTEGER,
            track_id   INTEGER,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        );
        """
    )
    conn.commit()

def get_data(endpoint: str):
    url = f"{base_url}/{endpoint}"
    items = []

    page = 1
    while True:
        resp = requests.get(url, params={"page": page})
        resp.raise_for_status()
        data = resp.json()
        items.extend(data["items"])

        if page >= data["pages"]:
            break
        page += 1

    return items


# ---------- Insertion en masse ----------
def insert_tracks(conn: sqlite3.Connection, tracks) -> None:
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT OR IGNORE INTO tracks
        (id, name, artist, songwriters, duration, genres, album, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                track["id"],
                track["name"],
                track["artist"],
                track["songwriters"],
                track["duration"],
                track["genres"],
                track["album"],
                track["created_at"],
                track["updated_at"],
            )
            for track in tracks
        ],
    )
    conn.commit()
    cur.close()


def insert_users(conn: sqlite3.Connection, users) -> None:
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT OR IGNORE INTO users
        (id, first_name, last_name, email, gender, favorite_genres, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                user["id"],
                user["first_name"],
                user["last_name"],
                user["email"],
                user["gender"],
                user["favorite_genres"],
                user["created_at"],
                user["updated_at"],
            )
            for user in users
        ],
    )
    conn.commit()
    cur.close()


def insert_listen_history(conn, histories) -> None:
    
    cur = conn.cursor()
    # Préparation : une ligne par (user_id, track_id)
    rows = []
    for hist in histories:
        user_id = hist["user_id"]
        created = hist["created_at"]
        updated = hist["updated_at"]
        for track_id in hist["items"]:
            rows.append((user_id, track_id, created, updated))

    cur.executemany(
        """
        INSERT INTO listen_history (user_id, track_id, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


# ---------- Fonction principale ----------
@repeat(every(24).hours)
def main() -> None:

    logging.info("Commence la récupération des données.")
    try:
        with sqlite3.connect(db_file) as conn:
            init_db(conn)

            logging.info("Récupération des tracks…")
            tracks = get_data("tracks")
            insert_tracks(conn, tracks)
            logging.info(f"{len(tracks)} tracks récupérés.")

            logging.info("Récupération des users…")
            users = get_data("users")
            insert_users(conn, users)
            logging.info(f"Récupéré {len(users)} users récupérés.")

            logging.info("Récupération des listen_history…")
            histories = get_data("listen_history")
            insert_listen_history(conn, histories)
            logging.info(f"{len(histories)} . historique d'écoute récupérés.")

        logging.info("All done ✅. Pipeline terminé avec succès.")
    except requests.exceptions.RequestException as e:
        logging.error(f"API echoué: {e}", exc_info=True)
    except sqlite3.Error as e:
        logging.error(f"Une erreur dans la base de données: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Une erreur inattendue dans le pipeline est survenue: {e}", exc_info=True)



if __name__ == "__main__":
    print("Démarrage de la récupération des données....")
    main()  
    while True:
        run_pending()
        time.sleep(3600) # Vérifie toutes les heures si une tâche est due



