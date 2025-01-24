import pytest
import requests
import pandas as pd
from unittest.mock import patch, Mock


from pipeline_etl.utils import fetch_all_pages, transform_listen_history, transform_tracks, transform_users


def test_fetch_all_pages_http_error():
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error"
    )

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_all_pages("http://any.com", {})


def test_transform_tracks():
    df = pd.DataFrame({"id": [1, 2], "duration": ["03:30", "04:45"]})
    transform_df = transform_tracks(df)

    assert "track_id" in transform_df.columns
    assert transform_df["duration"].to_list() == [210, 285]


def test_transform_users():
    df = pd.DataFrame(
        [
            {
                "id": 65989,
                "first_name": "Katelyn",
                "last_name": "Stevens",
                "email": "nicolehardy@example.org",
                "gender": "Genderqueer",
                "favorite_genres": "R&B",
                "created_at": "2024-06-18T21:04:43.263769",
                "updated_at": "2024-03-15T14:05:19.290732",
            },
            {
                "id": 38635,
                "first_name": "Kara",
                "last_name": "Sanchez",
                "email": "cainkathryn@example.com",
                "gender": "Genderfluid",
                "favorite_genres": "Rock",
                "created_at": "2024-06-14T00:37:49.611408",
                "updated_at": "2024-12-24T20:38:49.287025",
            },
        ]
    )
    transform_df = transform_users(df)

    assert "user_id" in transform_df.columns
    assert "first_name" not in transform_df.columns
    assert "last_name" not in transform_df.columns
    assert "email" not in transform_df.columns


def test_transform_listen_history():
    df = pd.DataFrame(
        [
            {
                "user_id": 65989,
                "items": [51363, 28379, 29805, 89972, 44713],
                "created_at": "2023-08-13T13:23:40.642525",
                "updated_at": "2024-04-18T09:40:26.968288",
            },
            {
                "user_id": 38635,
                "items": [37591, 16517, 56604, 51333, 99307],
                "created_at": "2024-04-19T00:57:32.854597",
                "updated_at": "2024-12-14T16:45:59.387171",
            },
        ]
    )
    transform_df = transform_listen_history(df)

    assert "tracks_id" in transform_df.columns
    assert transform_df["tracks_id"].to_list() == [
        "51363|28379|29805|89972|44713",
        "37591|16517|56604|51333|99307",
    ]
