import requests
import sqlite3
import logging

BASE_URL = "http://127.0.0.1:8000"
ENDPOINTS = {
    "tracks": "/tracks",
    "users": "/users",
    "listen_history": "/listen_history",
}
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def init_db(db_path="data.db"):
    """
    Initialize a SQLite database and create tables for tracks, users, and listens.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table for tracks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY,
            name TEXT,
            artist TEXT,
            songwriters TEXT,
            duration TEXT,
            genres TEXT,
            album TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')

    # Table for users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            gender TEXT,
            favorite_genres TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')

    # Table for listen history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listen_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            items TEXT,  -- you can store the list as a JSON string or CSV
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    return conn


def fetch_endpoint(endpoint: str) -> dict:
    """
    Fetch data from a given endpoint.
    The endpoints are expected to return a JSON document with a structure similar to:
      { "items": [...], "total": <int>, "page": <int>, "size": <int> }
    """
    url = BASE_URL + endpoint
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logging.info(f"Data successfully fetched from {url}")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return {}


def store_data(conn, data: list, table: str):
    """
    Store a list of dictionaries into the specified table.
    """
    if not data:
        logging.warning(f"No data to insert in table {table}.")
        return

    cursor = conn.cursor()
    if table == "tracks":
        for track in data:
            cursor.execute(
                """
                INSERT OR REPLACE INTO tracks 
                (id, name, artist, songwriters, duration, genres, album, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    track.get("id"),
                    track.get("name"),
                    track.get("artist"),
                    track.get("songwriters"),
                    track.get("duration"),
                    track.get("genres"),
                    track.get("album"),
                    track.get("created_at"),
                    track.get("updated_at"),
                ),
            )
    elif table == "users":
        for user in data:
            cursor.execute(
                """
                INSERT OR REPLACE INTO users 
                (id, first_name, last_name, email, gender, favorite_genres, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.get("id"),
                    user.get("first_name"),
                    user.get("last_name"),
                    user.get("email"),
                    user.get("gender"),
                    user.get("favorite_genres"),
                    user.get("created_at"),
                    user.get("updated_at"),
                ),
            )
    elif table == "listen_history":
        for item in data:
            items_str = None
            if item.get("items") is not None:
                import json
                items_str = json.dumps(item.get("items"))
            cursor.execute(
                """
                INSERT INTO listen_history (user_id, items, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    item.get("user_id"),
                    items_str,
                    item.get("created_at"),
                    item.get("updated_at"),
                ),
            )
    conn.commit()
    logging.info(f"Data inserted into {table} table.")


def run_pipeline(db_path="data.db"):
    """
    Runs the complete data pipeline:
     - Initializes the database
     - Fetches data from each endpoint
     - Stores data in the database
    """
    conn = init_db(db_path)

    # For each endpoint, fetch the data and store the items
    for key, endpoint in ENDPOINTS.items():
        json_response = fetch_endpoint(endpoint)
        items = json_response.get("items", [])
        store_data(conn, items, table=key)

    conn.close()
    logging.info("Pipeline executed successfully.")


if __name__ == "__main__":
    run_pipeline()
