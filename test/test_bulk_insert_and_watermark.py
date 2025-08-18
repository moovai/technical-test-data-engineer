import json

def test_bulk_insert_upsert_updates_only_if_newer(modules, tmp_path):
    load = modules.load

    # Insert initial row
    rows1 = [{"id": 10, "name": "A", "updated_at": "2025-08-01T10:00:00"}]
    load.bulk_insert("tracks", rows1)

    # Older update -> should be ignored
    rows2 = [{"id": 10, "name": "A-older", "updated_at": "2025-08-01T09:59:59"}]
    load.bulk_insert("tracks", rows2)

    # Newer update -> should overwrite
    rows3 = [{"id": 10, "name": "A-new", "updated_at": "2025-08-01T11:00:00"}]
    load.bulk_insert("tracks", rows3)

    # Read file
    path = load.TABLES["tracks"]["file"]
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "10" in data
    assert data["10"]["name"] == "A-new"

def test_watermark_roundtrip(modules):
    load = modules.load
    assert load.get_watermark("tracks") is None
    from datetime import datetime
    ts = datetime.fromisoformat("2025-08-01T11:00:00")
    load.set_watermark("tracks", ts)
    out = load.get_watermark("tracks")
    assert out == ts