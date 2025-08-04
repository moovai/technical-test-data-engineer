# test_sqlite_load.py
import sqlite3
import pytest
import pandas as pd
from transform import tracks_db, users_db, history_db

@pytest.fixture
def sqlite_conn():
    # Set up a fresh in-memory DB for each test
    conn = sqlite3.connect(':memory:')
    yield conn
    conn.close()

def test_sqlite_data_loading(sqlite_conn):
    conn = sqlite_conn
    cursor = conn.cursor()

    # Load and create tracks table
    tracks_df = tracks_db()
    assert not tracks_df.empty, "tracks_df is empty"

    cursor.execute("DROP TABLE IF EXISTS tracks")
    cursor.execute('''
        CREATE TABLE tracks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            artist TEXT,
            songwriters TEXT,
            duration TEXT,
            genres TEXT,
            album TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    for _, row in tracks_df.iterrows():
        cursor.execute('''
            INSERT INTO tracks (id, name, artist, songwriters, genres, album, created_at, updated_at, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))
    conn.commit()

    # Load and create users table
    users_df = users_db()
    assert not users_df.empty, "users_df is empty"

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            gender TEXT,
            favorite_genres TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    for _, row in users_df.iterrows():
        cursor.execute('''
            INSERT INTO users (id, first_name, last_name, email, gender, favorite_genres, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))
    conn.commit()

    # Load and create listen_history table
    history_df = history_db()
    assert not history_df.empty, "history_df is empty"

    cursor.execute("DROP TABLE IF EXISTS listen_history")
    cursor.execute('''
        CREATE TABLE listen_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (item_id) REFERENCES tracks(id)
        )
    ''')
    for _, row in history_df.iterrows():
        cursor.execute('''
            INSERT INTO listen_history (user_id, item_id, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', tuple(row))
    conn.commit()

    # ✅ Assert counts > 0
    cursor.execute("SELECT COUNT(*) FROM tracks")
    assert cursor.fetchone()[0] > 0

    cursor.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] > 0

    cursor.execute("SELECT COUNT(*) FROM listen_history")
    assert cursor.fetchone()[0] > 0