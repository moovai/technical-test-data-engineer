# test/test_run_fetch.py

import os
import json
from moovitamix_fastapi.run_fetch import fetch_and_save_all

def test_fetch_and_save_all(temp_data_dir, monkeypatch):
    
    def fake_fetch_data(endpoint):
        return [{"endpoint": endpoint}]
    
    monkeypatch.setattr("moovitamix_fastapi.api.client.fetch_data", fake_fetch_data)

    fetch_and_save_all(output_dir=temp_data_dir)

    for name in ["tracks.json", "users.json", "listen_history.json"]:
        path = os.path.join(temp_data_dir, name)
        assert os.path.exists(path)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, list)
