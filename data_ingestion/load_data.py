import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterable

from data_ingestion.fetch_data import retry_mechanism, iter_pages

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data_store"


PAGE_SIZE = 100

TABLES = {
    "tracks":         {"pk": "id",       "file": DATA_DIR / "tracks.json"},
    "users":          {"pk": "id",       "file": DATA_DIR / "users.json"},
    "listen_history": {"pk": "user_id",  "file": DATA_DIR / "listen_history.json"},
}

WATERMARK_FILE = DATA_DIR / "watermark.json" # This file stores the last processed row for each table. Will be used from incremental loads.

# -- functions for local storage -- #

def ensure_dirs():
    """
    Ensure that the data directory exists.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path, default):
    if not path.exists():
        return default # empty dict
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def to_dt(s):
    try:
        return datetime.fromisoformat(s) if s else None
    except Exception:
        return None

# -- watermarks -- #

def get_watermark(table_name):
    w = load_json(WATERMARK_FILE, {})
    value = w.get(table_name)
    return to_dt(value) if value else None 

def set_watermark(table_name, value: datetime):
    if value is None:
        return
    w = load_json(WATERMARK_FILE, {})
    w[table_name] = value.isoformat()
    save_json(WATERMARK_FILE, w)

# -- data ingestion -- #

def bulk_insert(table_name, rows: Iterable[Dict[str, Any]]):
    """
    Store data in a json file (one per table), keyed by the primary key.
    If key exists, it will be overwritten if updated_at is newer.
    """
    ensure_dirs()

    table = TABLES[table_name]
    file_path = table["file"]
    pk = table["pk"]

    stored = load_json(file_path, {})
    changed = False

    for row in rows:
        key = row.get(pk) 
        if key is None:
            continue
        if key not in stored:
            stored[key] = row
            changed = True
        else:
            current_updated_at = to_dt(stored[key].get("updated_at"))
            new_updated_at = to_dt(row.get("updated_at"))
            if current_updated_at is None or (new_updated_at and new_updated_at > current_updated_at):
                stored[key] = row
                changed = True
    if changed:
        save_json(file_path, stored)
        print(f"Inserted/updated {len(rows)} rows in {table_name} table.")


def incremental_load(endpoint, table_name):
    """
    Fetch data from the API endpoint and store it in the local file.
    This function will only insert new or updated rows based on the watermark.
    """
    ensure_dirs()

    last_watermark = get_watermark(table_name)
    max_wm = last_watermark

    with retry_mechanism() as sess:
        for page in iter_pages(endpoint, PAGE_SIZE):
            fresh_data = []
            for row in page.get("items", []):
                updated_at = to_dt(row.get("updated_at"))
                if last_watermark is None or (updated_at and updated_at > last_watermark):
                    fresh_data.append(row)
                    if max_wm is None or (updated_at and updated_at > max_wm):
                        max_wm = updated_at # to ensure we always keep the actual max upadted_at
            if fresh_data:
                bulk_insert(table_name, fresh_data)
            else:
                print(f"No new data found for {table_name} in this page.")
    
    set_watermark(table_name, max_wm) # updating the max updated_at in the watermark file.

def main():
    ensure_dirs()
    for table_name in TABLES:
        incremental_load(f"/{table_name}", table_name)

if __name__ == "__main__":
    main()

