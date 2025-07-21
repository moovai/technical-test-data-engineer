import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import json
import os
from unittest.mock import patch, Mock
from moovitamix_fastapi.data_pipeline import fetch_data, save_data
from requests.exceptions import RequestException

def test_fetch_data_success():
    mock_response = {"data": "example"}

    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_response

        result = fetch_data("tracks")
        assert result == mock_response
        mock_get.assert_called_once()

def test_fetch_data_failure():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = RequestException("API down")

        result = fetch_data("tracks")
        assert result is None

def test_save_data(tmp_path):
    data = {"test": 123}
    filename = "test_file.json"
    file_path = tmp_path / filename

    save_data(data, file_path)

    with open(file_path) as f:
        loaded = json.load(f)
        assert loaded == data