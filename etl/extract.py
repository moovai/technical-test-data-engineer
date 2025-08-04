import requests
import time 
import pandas as pd
MAX_RETRIES = 10
RETRY_DELAY = 3  # seconds
headers = {
    "Accept": "application/json"
}

def extract_data_from_api(url):
    """
    Attempts to extract data from a REST API with retry logic.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[Attempt {attempt}] Trying to connect to API...")
            response = requests.get(url, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            print(f"API not ready yet: {e}")
            time.sleep(RETRY_DELAY)
    return "Failed to connect to API after multiple attempts."
    
#extract tracks data
def get_tracks_data():
    all_tracks = []
    for i in range(11):  # pages 0 to 10
        url = f"http://api:8000/tracks?page={i}&size=100"
        response = extract_data_from_api(url)
        if response.status_code == 200:
            raw_tracks = response.json()
            items = raw_tracks.get("items", [])
            if items:
                all_tracks.extend(items)
        else:
            continue  # skip this page if there's an error
    #print(all_tracks)
    return pd.DataFrame(all_tracks)

#extract users data
def get_users_data():
    all_users = []
    for i in range(11):  # pages 0 to 10
        url = f"http://api:8000/users?page={i}&size=100"
        response = extract_data_from_api(url)
        if response.status_code == 200:
            raw_users = response.json()
            items = raw_users.get("items", [])
            if items:
                all_users.extend(items)
        else:
            continue  # skip this page if there's an error
    return pd.DataFrame(all_users)

#extract listen history data
def get_history_data():
    all_history = []
    for i in range(11):  # pages 0 to 10
        url = f"http://api:8000/listen_history?page={i}&size=100"
        response = extract_data_from_api(url)
        if response.status_code == 200:
            raw_history = response.json()
            items = raw_history.get("items")
            if items:
                all_history.extend(items)
        else:
            continue  # skip this page if there's an error
    return pd.DataFrame(all_history)
