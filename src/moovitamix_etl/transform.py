from uuid import UUID
import pandas as pd


def transform_tracks(tracks: dict, id: UUID) -> pd.DataFrame:
    """
    Transform the tracks data by adding a new column 'track_length' and setting it to 0.
    """
    data_df = pd.DataFrame(tracks)
    data_df["run_id"] = str(id)
    return data_df


def transform_users(users: dict, id: UUID) -> pd.DataFrame:
    """
    Transform the users data by adding a new column 'is_active' and setting it to True.
    """
    data_df = pd.DataFrame(users)
    data_df["run_id"] = str(id)
    return data_df


def transform_listen_history(listen_history: dict, id: UUID) -> pd.DataFrame:
    """
    Transform the listen history data by adding a new column 'is_listened' and setting it to True.
    """
    data_df = pd.DataFrame(listen_history)
    data_df["run_id"] = str(id)
    return data_df