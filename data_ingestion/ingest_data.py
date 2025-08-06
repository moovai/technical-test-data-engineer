import requests
import pandas as pd
from loguru import logger

BASE_URL = "http://127.0.0.1:8001"

def get_users():
    """Fetches all users from the API and returns them as a pandas DataFrame."""
    all_users = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}/users?page={page}&size=100")
        if response.status_code == 200:
            data = response.json()
            users = data["items"]
            if not users:
                break
            all_users.extend(users)
            page += 1
            logger.info(f"Fetched page {page} of users, total users fetched: {len(all_users)}")
        else:
            logger.warning(f"Failed to fetch users: {response.status_code}")
            logger.error(f"Error details: {response.text}")
            break
    return pd.DataFrame(all_users)


def get_tracks():
    """Fetches all tracks from the API and returns them as a pandas DataFrame."""
    all_tracks = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}/tracks?page={page}&size=100")
        if response.status_code == 200:
            data = response.json()
            tracks = data["items"]
            if not tracks:
                break
            all_tracks.extend(tracks)
            page += 1
            logger.info(f"Fetched page {page} of tracks, total tracks fetched: {len(all_tracks)}")
        else:
            logger.warning(f"Failed to fetch tracks: {response.status_code}")
            logger.error(f"Error details: {response.text}")
            break
    return pd.DataFrame(all_tracks)

def get_listen_history():
    """Fetches all listen history from the API and returns it as a pandas DataFrame."""
    all_listen_history = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}/listen_history?page={page}&size=100")
        if response.status_code == 200:
            data = response.json()
            listen_history = data["items"]
            if not listen_history:
                break
            all_listen_history.extend(listen_history)
            page += 1
            logger.info(f"Fetched page {page} of listen history, total records fetched: {len(all_listen_history)}")    
        else:
            logger.warning(f"Failed to fetch listen history: {response.status_code}")
            logger.error(f"Error details: {response.text}")
            break
    return pd.DataFrame(all_listen_history)

def main():
    """init  log file """
    logger.add("data_ingestion.log", rotation="1 MB", level="INFO")
    logger.info("Starting data ingestion process")  
    logger.info("##########################################################################")
    """Main function to ingest data from all endpoints."""
    users_df = get_users()
    tracks_df = get_tracks()
    listen_history_df = get_listen_history()

    print("Users DataFrame:")
    print(users_df.head())
    print("\nTracks DataFrame:")
    print(tracks_df.head())
    print("\nListen History DataFrame:")
    print(listen_history_df.head())
    logger.info("Data ingestion process completed successfully")
    logger.info("##########################################################################")

if __name__ == "__main__":
    main()
