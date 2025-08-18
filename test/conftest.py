import os
import json
import pytest
import types
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_environment(tmp_path, monkeypatch):
    # Create a temporary data_store directory
    # Set the BASE_URL environment variable for testing. Fake URL.
    monkeypatch.setenv("BASE_URL", "http://testserver:8000") 

    from data_ingestion import load_data

    # Create temporary data_store directory
    test_data_dir = tmp_path / "data_store"
    test_data_dir.mkdir(parents=True, exist_ok=True)    


    monkeypatch.setattr(load_data, "DATA_DIR", test_data_dir, raising=False)
    monkeypatch.setattr(load_data, "WATERMARK_FILE", test_data_dir / "watermark.json", raising=False)

    test_tables = {}
    for name, info in load_data.TABLES.items():
        test_tables[name] = {
            "pk": info["pk"],
            "file": test_data_dir / f"{name}.json"
        }
    monkeypatch.setattr(load_data, "TABLES", test_tables, raising=False)

    yield

@pytest.fixture
def fake_session(monkeypatch):
    class FakeResp:
        def __init__(self, payload):
            self._payload = payload
            self.status_code = 200
        def raise_for_status(self): pass
        def json(self): return self._payload

    class FakeSession:
        def __init__(self): self.get = None
        def __enter__(self): return self
        def __exit__(self, *a): pass

    fs = FakeSession()
    fs.FakeResp = FakeResp

    # Import once here so we can patch
    import data_ingestion.fetch_data as fetch
    monkeypatch.setattr(fetch, "retry_mechanism", lambda *a, **k: fs)

    return fs

@pytest.fixture
def modules():
    # Handy re-imports
    from data_ingestion import fetch_data, load_data
    return types.SimpleNamespace(fetch=fetch_data, load=load_data)