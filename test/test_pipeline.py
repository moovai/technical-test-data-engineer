import os
import tempfile
import json
import pytest
from src.moovitamix_fastapi.pipeline import init_db, store_data

# Sample data for testing
sample_tracks = [
    {
        "id": 1,
        "name": "Track One",
        "artist": "Artist A",
        "songwriters": "Writer A",
        "duration": "03:45",
        "genres": "Pop",
        "album": "Album One",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-02T12:00:00"
    }
]

sample_users = [
    {
        "id": 101,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "gender": "Male",
        "favorite_genres": "Rock",
        "created_at": "2023-01-03T12:00:00",
        "updated_at": "2023-01-04T12:00:00"
    }
]

sample_listen_history = [
    {
        "user_id": 101,
        "items": [1, 2, 3],
        "created_at": "2023-01-05T12:00:00",
        "updated_at": "2023-01-06T12:00:00"
    }
]

@pytest.fixture
def temp_db():
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    yield db_path
    os.remove(db_path)

def test_init_db(temp_db):
    conn = init_db(temp_db)
    cursor = conn.cursor()
    for table in ["tracks", "users", "listen_history"]:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        assert cursor.fetchone() is not None, f"Table {table} should exist"
    conn.close()

def test_store_data_tracks(temp_db):
    conn = init_db(temp_db)
    store_data(conn, sample_tracks, "tracks")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks WHERE id=?", (1,))
    row = cursor.fetchone()
    assert row is not None, "Track should have been inserted"
    conn.close()

def test_store_data_users(temp_db):
    conn = init_db(temp_db)
    store_data(conn, sample_users, "users")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (101,))
    row = cursor.fetchone()
    assert row is not None, "User should have been inserted"
    conn.close()

def test_store_data_listen_history(temp_db):
    conn = init_db(temp_db)
    store_data(conn, sample_listen_history, "listen_history")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listen_history WHERE user_id=?", (101,))
    row = cursor.fetchone()
    assert row is not None, "Listen history record should have been inserted"
    # Verify that items were stored as JSON (or a string that decodes to a list)
    items_str = row[2]
    items = json.loads(items_str)
    assert isinstance(items, list)
    conn.close()
