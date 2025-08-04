import pandas as pd
from unittest.mock import patch, MagicMock

# Import the script to be tested
from data_ingestion.ingest_data import get_listen_history, get_tracks, get_users

# --- Expected Schemas ---
EXPECTED_USERS_COLUMNS = [
    "id",
    "first_name",
    "last_name",
    "email",
    "gender",
    "favorite_genres",
    "created_at",
    "updated_at",
]
EXPECTED_TRACKS_COLUMNS = [
    "id",
    "name",
    "artist",
    "songwriters",
    "duration",
    "genres",
    "album",
    "created_at",
    "updated_at",
]
EXPECTED_LISTEN_HISTORY_COLUMNS = [
    "id",
    "user_id",
    "track_id",
    "listened_at",
    "created_at",
    "updated_at",
]


# --- Mock Setup ---
def mock_success_response(sample_data, page=1):
    """Creates a mock response object for a successful API call."""
    mock_res = MagicMock()
    mock_res.status_code = 200

    def json_func():
        # Simulate pagination: return data for page 1, empty list for subsequent pages
        return {"items": sample_data if page == 1 else []}

    mock_res.json = json_func
    return mock_res


# Sample data that matches the expected schemas
users_sample_data = [{col: "sample" for col in EXPECTED_USERS_COLUMNS}]
tracks_sample_data = [{col: "sample" for col in EXPECTED_TRACKS_COLUMNS}]
listen_history_sample_data = [
    {col: "sample" for col in EXPECTED_LISTEN_HISTORY_COLUMNS}
]

# --- Original Mock Tests (verifying DataFrame content) ---


@patch("data_ingestion.ingest_data.requests.get")
def test_get_users(mock_get):
    """Tests the get_users function returns a DataFrame with expected content."""
    mock_get.side_effect = [
        mock_success_response(users_sample_data, page=1),
        mock_success_response([], page=2),
    ]
    users_df = get_users()
    assert isinstance(users_df, pd.DataFrame)
    assert not users_df.empty
    # Check that the content matches the sample data
    assert users_df.to_dict("records") == users_sample_data
    mock_get.assert_any_call("http://127.0.0.1:8001/users?page=1&size=100")


@patch("data_ingestion.ingest_data.requests.get")
def test_get_tracks(mock_get):
    """Tests the get_tracks function returns a DataFrame with expected content."""
    mock_get.side_effect = [
        mock_success_response(tracks_sample_data, page=1),
        mock_success_response([], page=2),
    ]
    tracks_df = get_tracks()
    assert isinstance(tracks_df, pd.DataFrame)
    assert not tracks_df.empty
    assert tracks_df.to_dict("records") == tracks_sample_data
    mock_get.assert_any_call("http://127.0.0.1:8001/tracks?page=1&size=100")


@patch("data_ingestion.ingest_data.requests.get")
def test_get_listen_history(mock_get):
    """Tests the get_listen_history function returns a DataFrame with expected content."""
    mock_get.side_effect = [
        mock_success_response(listen_history_sample_data, page=1),
        mock_success_response([], page=2),
    ]
    listen_history_df = get_listen_history()
    assert isinstance(listen_history_df, pd.DataFrame)
    assert not listen_history_df.empty
    assert listen_history_df.to_dict("records") == listen_history_sample_data
    mock_get.assert_any_call("http://127.0.0.1:8001/listen_history?page=1&size=100")


# --- New Schema Validation Tests ---


@patch("data_ingestion.ingest_data.requests.get")
def test_get_users_schema(mock_get):
    """Tests that the DataFrame from get_users has the expected columns."""
    mock_get.return_value = mock_success_response(users_sample_data)
    users_df = get_users()
    assert set(users_df.columns) == set(EXPECTED_USERS_COLUMNS)


@patch("data_ingestion.ingest_data.requests.get")
def test_get_tracks_schema(mock_get):
    """Tests that the DataFrame from get_tracks has the expected columns."""
    mock_get.return_value = mock_success_response(tracks_sample_data)
    tracks_df = get_tracks()
    assert set(tracks_df.columns) == set(EXPECTED_TRACKS_COLUMNS)


@patch("data_ingestion.ingest_data.requests.get")
def test_get_listen_history_schema(mock_get):
    """Tests that the DataFrame from get_listen_history has the expected columns."""
    mock_get.return_value = mock_success_response(listen_history_sample_data)
    listen_history_df = get_listen_history()
    assert set(listen_history_df.columns) == set(EXPECTED_LISTEN_HISTORY_COLUMNS)