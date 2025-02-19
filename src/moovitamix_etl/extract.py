import os
import requests
import logging

MOOVITAMIX_API_URL = os.getenv("MOOVITAMIX_API_URL", "http://127.0.0.1:8000")

def fetch_moovitamix_data(endpoint: str, batch_size: int = 100):
    logging.info(f"Fetching data from {endpoint} - batch size: {batch_size}")
    page = 1
    items = []
    try:
        while True:
            response = requests.get(f"{MOOVITAMIX_API_URL}/{endpoint}", params={"page": page, "size": batch_size})
            data = response.json()

            if response.status_code != 200 or not data["items"]:
                break
            items.extend(data["items"])
            page+=1
    except Exception as e:
        logging.error(f"Error fetching data from {endpoint}: {e}")
        
    logging.info(f"Retrieved {len(items)} items")
    return items

def extract_moovitamix_tracks():
    return fetch_moovitamix_data("tracks")

def extract_moovitamix_users():
    return fetch_moovitamix_data("users")

def extract_moovitamix_listen_history():
    return fetch_moovitamix_data("listen_history")