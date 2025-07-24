import sqlite3
from unittest.mock import MagicMock, patch
import requests

import pytest

from src.pipeline.fetch import (
    get_data,
    insert_listen_history,
    insert_tracks,
    insert_users,
    init_db,
)


@pytest.fixture
def db_conn():
    """Fixture Pytest pour une base de données SQLite en mémoire propre pour chaque test."""
    # Utiliser :memory: pour une base de données en mémoire, rapide et propre.
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    yield conn
    conn.close()


def test_init_db_creates_tables(db_conn):
    """Vérifie que toutes les tables sont créées par init_db."""
    cur = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = {row[0] for row in cur.fetchall()}
    assert {"tracks", "users", "listen_history"}.issubset(tables)


@pytest.mark.parametrize(
    "test_id, mock_responses_json, expected_result, expected_exception",
    [
        pytest.param(
            "pagination",
            [
                {"pages": 2, "items": [{"id": 1, "name": "A"}]},
                {"pages": 2, "items": [{"id": 2, "name": "B"}]},
            ],
            [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
            None,
            id="cas_pagination",
        ),
        pytest.param(
            "single_page",
            [{"pages": 1, "items": [{"id": 1}, {"id": 2}]}],
            [{"id": 1}, {"id": 2}],
            None,
            id="cas_page_unique",
        ),
        pytest.param(
            "empty_response", [{"pages": 1, "items": []}], [], None, id="cas_reponse_vide"
        ),
        pytest.param(
            "http_error",
            [],
            None,
            requests.exceptions.HTTPError("Simulated HTTP Error"),
            id="cas_erreur_http",
        ),
    ],
)
@patch("src.pipeline.fetch.requests.get")
def test_get_data_scenarios(mock_get, test_id, mock_responses_json, expected_result, expected_exception):
    """Vérifie le comportement de get_data dans divers scénarios."""
    if expected_exception:
        mock_get.return_value.raise_for_status.side_effect = expected_exception
        with pytest.raises(type(expected_exception)):
            get_data("some_endpoint")
        return

    mock_responses = []
    for json_data in mock_responses_json:
        mock_resp = MagicMock()
        mock_resp.json.return_value = json_data
        mock_resp.raise_for_status.return_value = None
        mock_responses.append(mock_resp)
    mock_get.side_effect = mock_responses

    items = get_data("some_endpoint")

    assert items == expected_result
    assert mock_get.call_count == len(mock_responses_json)

def test_insert_tracks(db_conn):
    """Vérifie que les données des morceaux sont correctement insérées."""
    tracks_data = [
        {
            "id": 1, "name": "Song A", "artist": "Artist 1", "songwriters": "Writer 1",
            "duration": 180, "genres": "Pop", "album": "Album X",
            "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"
        }
    ]
    insert_tracks(db_conn, tracks_data)

    cur = db_conn.execute("SELECT id, name, artist FROM tracks WHERE id = 1")
    row = cur.fetchone()
    assert row is not None
    assert row == (1, "Song A", "Artist 1")


def test_insert_users(db_conn):
    """Vérifie que les données des utilisateurs sont correctement insérées."""
    users_data = [
        {
            "id": 1, "first_name": "John", "last_name": "Doe", "email": "john@test.com",
            "gender": "Male", "favorite_genres": "Rock",
            "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00"
        }
    ]
    insert_users(db_conn, users_data)

    cur = db_conn.execute("SELECT id, first_name, email FROM users WHERE id = 1")
    row = cur.fetchone()
    assert row is not None
    assert row == (1, "John", "john@test.com")


def test_insert_listen_history_flattens_data(db_conn):
    """Vérifie que l'historique d'écoute est aplati et inséré correctement."""
    # Pré-requis : insérer un utilisateur et des morceaux pour satisfaire les clés étrangères
    insert_users(db_conn, [{"id": 10, "first_name": "Test", "last_name": "User", "email": "a@b.c", "gender": "NA", "favorite_genres": "NA", "created_at": "...", "updated_at": "..."}])
    insert_tracks(db_conn, [
        {"id": 100, "name": "t1", "artist": "a1", "songwriters": "s1", "duration": 1, "genres": "g1", "album": "al1", "created_at": "...", "updated_at": "..."},
        {"id": 101, "name": "t2", "artist": "a2", "songwriters": "s2", "duration": 2, "genres": "g2", "album": "al2", "created_at": "...", "updated_at": "..."}
    ])

    histories_data = [
        {
            "user_id": 10,
            "items": [100, 101],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
    ]
    insert_listen_history(db_conn, histories_data)

    cur = db_conn.execute(
        "SELECT user_id, track_id FROM listen_history ORDER BY track_id"
    )
    rows = cur.fetchall()
    assert len(rows) == 2
    assert rows == [(10, 100), (10, 101)]