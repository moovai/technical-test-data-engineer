import pytest
import pandas as pd
import os
from pathlib import Path

@pytest.fixture(scope="session")
def data_dir():
    return Path("/app/data")    

@pytest.fixture
def run_timestamp(data_dir, scope="session"):
    with open(data_dir / "latest_run.txt", "r") as f:
        return f.read().strip()

@pytest.fixture
def data_frames(data_dir, run_timestamp, scope="session"):
    tracks_df = pd.read_csv(data_dir / f"tracks_{run_timestamp}.csv")
    users_df = pd.read_csv(data_dir / f"users_{run_timestamp}.csv")
    listen_history_df = pd.read_csv(data_dir / f"listen_history_{run_timestamp}.csv")
    return tracks_df, users_df, listen_history_df

def test_csv_files_existence(data_dir, run_timestamp):
    """
    Test the existence of the expected csv files
    """
    expected_files = [
        f"tracks_{run_timestamp}.csv",
        f"users_{run_timestamp}.csv",
        f"listen_history_{run_timestamp}.csv"
    ]
    
    for file in expected_files:
        assert (data_dir / file).exists(), f"File {file} does not exist"

def test_csv_data_integrity(data_frames):
    """
    Test the integrity of the data in the files
    Ensure length of each file is what's expected.
    In our case, hardcoded to 1000 rows.
    """
    tracks_df, users_df, listen_history_df = data_frames
    
    assert len(tracks_df) == 1000, f"Expected 1000 tracks, got {len(tracks_df)}"
    assert len(users_df) == 1000, f"Expected 1000 users, got {len(users_df)}"
    assert len(listen_history_df) == 1000, f"Expected 1000 listen history entries, got {len(listen_history_df)}"

def test_data_relationships(data_frames):
    """
    Test the relationships between the data in the files
    """
    tracks_df, users_df, listen_history_df = data_frames
    
    all_user_ids = set(users_df['id'])
    listen_history_user_ids = set(listen_history_df['user_id'])
    assert listen_history_user_ids.issubset(all_user_ids), \
        "Found user_ids in listen_history that don't exist in users"
    
    all_track_ids = set(tracks_df['id'])
    
    listen_history_track_ids = set()
    for track_list in listen_history_df['items']:
        track_ids = eval(track_list) 
        listen_history_track_ids.update(track_ids)
    
    assert listen_history_track_ids.issubset(all_track_ids), \
        "Found track_ids in listen_history that don't exist in tracks"

def test_data_types(data_frames):
    """
    Test the types of the data in the files
    """
    tracks_df, users_df, listen_history_df = data_frames
    
    assert tracks_df['id'].dtype in ['int64', 'int32'], "Track ID should be integer"
    assert tracks_df['duration'].dtype == 'object', "Duration should be string"
    
    assert users_df['id'].dtype in ['int64', 'int32'], "User ID should be integer"
    assert users_df['email'].dtype == 'object', "Email should be string"
    
    assert listen_history_df['user_id'].dtype in ['int64', 'int32'], "User ID should be integer"
    assert listen_history_df['items'].dtype == 'object', "Items should be string"

def test_data_quality(data_frames):
    """
    Test the quality of the data in the files
    """
    tracks_df, users_df, listen_history_df = data_frames
    
    assert not tracks_df.isnull().any().any(), "Found null values in tracks.csv"
    assert not users_df.isnull().any().any(), "Found null values in users.csv"
    assert not listen_history_df.isnull().any().any(), "Found null values in listen_history.csv"
    
    assert users_df['email'].str.contains('@').all(), "Found invalid email formats"
    
    assert tracks_df['duration'].str.match(r'^\d{1,2}:\d{2}$').all(), \
        "Found invalid duration formats"