import pytest
import requests

BASE_URL = "http://127.0.0.1:8001"

@pytest.mark.parametrize("endpoint", ["/users", "/tracks", "/listen_history"])
def test_endpoint_returns_200(endpoint):
    """
    Tests that the API endpoints return a 200 OK status code.
    """
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 200
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to {BASE_URL} failed: {e}")

