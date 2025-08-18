import json
from datetime import datetime

def test_incremental_load_is_idempotent_no_duplicates(fake_session, modules):
    load = modules.load

    # Seed store and watermark
    seed_ts = "2025-08-01T12:00:00"
    load.bulk_insert("tracks", [{"id": 42, "name": "seed", "updated_at": seed_ts}])
    load.set_watermark("tracks", datetime.fromisoformat(seed_ts))

    # Same record again (same ts) then an older one → both ignored
    def fake_get(url, params=None, timeout=None):
        page = params["page"]
        if page == 1:
            return fake_session.FakeResp({
                "items": [{"id": 42, "name": "seed", "updated_at": seed_ts}],
                "pages": 2,
            })
        elif page == 2:
            return fake_session.FakeResp({
                "items": [{"id": 42, "name": "seed", "updated_at": "2025-08-01T11:00:00"}],
                "pages": 2,
            })
        else:
            raise AssertionError("Should not request page > 2")

    fake_session.get = fake_get

    # Running once should be enough, but still want to check if the pipeline is re-triggered with the same input the state remains unchanged. 
    # Reason why running twice here.
    load.incremental_load("tracks", "tracks")
    load.incremental_load("tracks", "tracks")

    # Validate: still a single record, unchanged
    path = load.TABLES["tracks"]["file"]
    data = json.loads(path.read_text(encoding="utf-8"))
    assert list(map(int, data.keys())) == [42]
    assert data["42"]["name"] == "seed"
    assert data["42"]["updated_at"] == seed_ts

    # Watermark unchanged (no newer data seen)
    wm = load.get_watermark("tracks")
    assert wm.isoformat() == seed_ts