# test/test_file_writer.py
import os
import json
from moovitamix_fastapi.utils.file_writer import save_data_to_json

def test_save_data_to_json_creates_file(temp_data_dir):
    data = [{"id": 1, "name": "test"}]
    filename = "test.json"

    save_data_to_json(filename, data, output_dir=temp_data_dir)

    file_path = os.path.join(temp_data_dir, filename)
    assert os.path.exists(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    
    assert saved_data == data