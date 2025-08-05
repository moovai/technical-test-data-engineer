# test/test_routes.py

from fastapi.testclient import TestClient
from moovitamix_fastapi.main import app

client = TestClient(app)

def test_get_tracks():
    response = client.get("/tracks")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_listen_history():
    response = client.get("/listen_history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
