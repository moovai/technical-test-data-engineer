# src/moovitamix_fastapi/api/client.py

import requests
from moovitamix_fastapi.config import BASE_API_URL

def fetch_data(endpoint: str) -> list:
    url = f"{BASE_API_URL}{endpoint}"
    response = requests.get(url, params={"page": 1, "size": 100})
    response.raise_for_status()
    return response.json()["items"]