import requests
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
ENDPOINTS = ["tracks", "users", "listen_history"]
OUTPUT_DIR = "data_output"

def fetch_and_store_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Save to JSON file
        with open(f"{OUTPUT_DIR}/{endpoint}_{timestamp}.json", "w") as f:
            json.dump(data, f, indent=2)

    print("Data pipeline executed successfully.")

if __name__ == "__main__":
    fetch_and_store_data()
