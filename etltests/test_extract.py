import requests

###add handling multiple pages
def test_tracks_endpoint():
    response = requests.get("http://api:8000/tracks")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)


def test_users_endpoint():
    response = requests.get("http://api:8000/users")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)


def test_history_endpoint():
    response = requests.get("http://api:8000/listen_history")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)