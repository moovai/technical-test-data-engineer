# src/moovitamix_fastapi/run_fetch.py

from moovitamix_fastapi.api.client import fetch_data
from moovitamix_fastapi.utils.file_writer import save_data_to_json
from moovitamix_fastapi.config import DATA_DIR  

def fetch_and_save_all(output_dir=None):
    output_dir = output_dir or DATA_DIR  
    for endpoint, filename in {
        "/tracks": "tracks.json",
        "/users": "users.json",
        "/listen_history": "listen_history.json"
    }.items():
        print(f"Récupération des données depuis {endpoint}...")
        data = fetch_data(endpoint)
        save_data_to_json(filename, data, output_dir=output_dir)
        print(f"Données enregistrées dans {output_dir}/{filename}")

if __name__ == "__main__":
    fetch_and_save_all()
