import json
from datetime import datetime

def test_incremental_load_filters_by_watermark_and_updates_it(fake_session, modules):
    fetch, load = modules.fetch, modules.load

    # Seed watermark so we only accept rows with updated_at > 2025-08-01T12:00:00
    load.set_watermark("tracks", datetime.fromisoformat("2025-08-01T12:00:00"))

    # Fake paginated responses keyed off the requested page number
    def fake_get(url, params=None, timeout=None):
        page = params["page"]
        if page == 1:
            return fake_session.FakeResp({
                "items": [
                    {"id": 1, "name": "old",  "updated_at": "2025-08-01T11:59:59"},  # ignored
                    {"id": 2, "name": "new1", "updated_at": "2025-08-01T12:00:01"},  # ingested
                ],
                "pages": 2,
            })
        elif page == 2:
            return fake_session.FakeResp({
                "items": [
                    {"id": 3, "name": "new2", "updated_at": "2025-08-01T12:30:00"},  # ingested
                ],
                "pages": 2,
            })
        else:
            raise AssertionError("Should not request page > 2")

    fake_session.get = fake_get

    # Run incremental load
    load.incremental_load("tracks", "tracks")

    # Verify stored file contains only ids 2 and 3
    data = json.loads(load.TABLES["tracks"]["file"].read_text(encoding="utf-8"))
    assert set(map(int, data.keys())) == {2, 3}

    # Verify watermark advanced to the max updated_at
    wm = load.get_watermark("tracks")
    assert wm.isoformat() == "2025-08-01T12:30:00"