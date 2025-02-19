import pytest
from src.moovitamix_etl.extract import extract_moovitamix_tracks, extract_moovitamix_users, extract_moovitamix_listen_history
from src.moovitamix_etl.load import create_db_connection, init_database, delete_database, load_listen_history, load_tracks, load_users

test_db = "test.db"

mock_tracks = [
    {
        "id": 1,
        "name": "Track 1",
        "artist": "Artist 1",
        "songwriters": "Songwriter 1",
        "duration": "3:00",
        "genres": "Pop",
        "album": "Album 1",
        "created_at": "2021-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00"
    },
    {
        "id": 2,
        "name": "Track 2",
        "artist": "Artist 2",
        "songwriters": "Songwriter 2",
        "duration": "4:00",
        "genres": "Rock",
        "album": "Album 2",
        "created_at": "2021-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00"
    }
]

mock_users = [
    {
        "id": 1,
        "first_name": "First 1",
        "last_name": "Last 1",
        "email": "first1.last1@example",
    }
]

mock_listen_history = [
    {
        "user_id": 1,
        "items": [
            2, 1
        ]
    }
]

@pytest.fixture
def setup_database():
    init_database(test_db)
    yield
    delete_database(test_db)
    
def test_fetch_tracks():
    tracks = extract_moovitamix_tracks()
    assert len(tracks) > 0
    assert all(isinstance(track, dict) for track in tracks)
    
def test_fetch_users():
    users = extract_moovitamix_users()
    assert len(users) > 0
    assert all(isinstance(user, dict) for user in users)
    
def test_fetch_listen_history():
    listen_history = extract_moovitamix_listen_history()
    assert len(listen_history) > 0
    assert all(isinstance(history, dict) for history in listen_history)
     
def test_load_tracks():
    init_database(test_db)

    conn = create_db_connection()
    load_tracks(mock_tracks, conn)
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    delete_database(test_db)
    assert len(result) == len(mock_tracks)
    
def test_load_users():
    init_database(test_db)
    conn = create_db_connection()
    load_users(mock_tracks, conn)
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    delete_database(test_db)

    assert len(result) == len(mock_tracks)
    
def test_load_listen_history():
    init_database(test_db)
    conn = create_db_connection()
    load_listen_history(mock_listen_history, conn)
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listen_history")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    delete_database(test_db)
    assert len(result) == len(mock_listen_history)
    