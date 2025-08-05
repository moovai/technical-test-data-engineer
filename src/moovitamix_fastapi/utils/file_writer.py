# src/moovitamix_fastapi/utils/file_writer.py

import os
import json
from moovitamix_fastapi.config import DATA_DIR

def save_data_to_json(filename: str, data: list, output_dir: str = DATA_DIR):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


