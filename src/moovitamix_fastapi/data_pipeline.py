import requests
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "data"

ENDPOINTS = ["tracks", "users", "listen_history"]

def fetch_data(endpoint: str, page: int = 1, size: int = 100):
    url = f"{BASE_URL}/{endpoint}?page={page}&size={size}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def save_data(data, filename: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)

def run_pipeline():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for endpoint in ENDPOINTS:
        data = fetch_data(endpoint)
        if data is not None:
            save_data(data, f"{endpoint}_{timestamp}.json")

if __name__ == "__main__":
    run_pipeline()
