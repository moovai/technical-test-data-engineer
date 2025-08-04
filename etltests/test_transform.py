import pytest
import pandas as pd
import numpy as np
from etl.transform import (
    clean_text_series,
    parse_datetime_series,
    duration_to_seconds_series,
    transform_tracks_df,
    transform_users_df,
    transform_history_df,
)

def test_clean_text_series():
    series = pd.Series(["  Hello!  ", None, "WoRLD!!"])
    cleaned = clean_text_series(series)
    expected = pd.Series(["hello", np.nan, "world"])
    pd.testing.assert_series_equal(cleaned, expected)


def test_parse_datetime_series():
    series = pd.Series(["2023-08-03 04:00:01", "invalid", None])
    parsed = parse_datetime_series(series)
    expected = pd.Series(["2023-08-03 04:00:01", np.nan, np.nan])
    assert parsed.tolist() == expected.tolist()


def test_duration_to_seconds_series():
    series = pd.Series(["03:15", "00:30", "bad"])
    seconds = duration_to_seconds_series(series)
    expected = pd.Series([195, 30, np.nan])
    pd.testing.assert_series_equal(seconds, expected)


def test_transform_tracks_df():
    raw = pd.DataFrame([{
        "id": 1,
        "name": "  Song A ",
        "artist": "ARTIST",
        "songwriters": "WRITER",
        "genres": "Pop",
        "album": "ALBUM",
        "duration": "02:30",
        "created_at": "2024-08-03 03:00:00",
        "updated_at": "2024-08-03 04:00:00"
    }])
    transformed = transform_tracks_df(raw)
    assert "duration_seconds" in transformed.columns
    assert transformed["duration_seconds"].iloc[0] == 150


def test_transform_users_df():
    raw = pd.DataFrame([{
        "id": 1,
        "first_name": " Alice ",
        "last_name": " Smith ",
        "email": "TEST@EMAIL.com",
        "gender": "FEMALE",
        "favorite_genres": "Jazz",
        "created_at": "2024-08-03 03:00:00",
        "updated_at": "2024-08-03 04:00:00"
    }])
    transformed = transform_users_df(raw)
    assert transformed["first_name"].iloc[0] == "alice"
    assert transformed["email"].iloc[0] == "test@emailcom"

def test_transform_history_df():
    raw = pd.DataFrame([{
        "user_id": 123,
        "items": [101, -5, "bad", 102],
        "created_at": "2024-08-03 01:00:00",
        "updated_at": "2024-08-03 02:00:00"
    }])
    transformed = transform_history_df(raw)
    assert len(transformed) == 2  # only 101 and 102 are valid
    assert all(transformed["item"].isin([101, 102]))