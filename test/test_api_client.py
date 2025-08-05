# test/test_api_client.py

import pytest
from moovitamix_fastapi.api.client import fetch_data

def test_fetch_data_success(monkeypatch):
    """Teste la récupération des données avec un endpoint valide"""

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"items": [{"id": 1, "name": "test track"}]}

    def mock_get(url, params):
        return MockResponse()

    monkeypatch.setattr("moovitamix_fastapi.api.client.requests.get", mock_get)

    result = fetch_data("/tracks")
    assert isinstance(result, list)
    assert result[0]["name"] == "test track"

def test_fetch_data_invalid_endpoint(monkeypatch):
    """Teste la gestion d'une erreur HTTP """

    class MockResponse:
        def raise_for_status(self):
            raise Exception("404 Not Found")

    def mock_get(url, params):
        return MockResponse()

    monkeypatch.setattr("moovitamix_fastapi.api.client.requests.get", mock_get)

    with pytest.raises(Exception):
        fetch_data("/invalid_endpoint")
