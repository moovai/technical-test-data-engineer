import src.pipeline.client as client_mod
from src.pipeline.normalize import norm_track, norm_user, norm_listen
import src.pipeline.main as main_mod
from pathlib import Path
import pandas as pd
import httpx
import respx


def test_iter_paginated(monkeypatch):
    monkeypatch.setattr(client_mod, "API_BASE_URL", "http://testserver")

    with respx.mock(base_url="http://testserver") as mock:
        mock.get("/tracks").mock(
            side_effect=[
                httpx.Response(200, json={"items": [{"id": 1}, {"id": 2}]}),
                httpx.Response(200, json={"items": [{"id": 3}]}),
            ]
        )
        rows = list(client_mod.iter_paginated("/tracks", size=2))
        assert [r["id"] for r in rows] == [1, 2, 3]


def test_norm_track():
    raw = {
        "id": 25827,
        "name": "Marea (We’ve Lost Dancing)",
        "artist": "Fred again",
        "duration": "4:45",
        "genres": "electro",
        "album": "prout",
        "created_at": "2025-05-20T13:04:46.091922",
        "updated_at": "2025-06-08T11:34:58.812509",
    }
    out = norm_track(raw)
    assert out["id"] == 25827
    assert out["title"] == "Marea (We’ve Lost Dancing)"
    assert out["artist"] == "Fred again"
    assert out["duration"] == "4:45"
    assert out["genres"] == "electro"
    assert out["album"] == "prout"


def test_norm_user():
    raw = {
        "id": 15278,
        "email": "dede@gmail.com",
        "first_name": "Dede",
        "last_name": "Labidouille",
        "gender": "homme",
        "favorite_genres": "femme",
        "created_at": "2024-02-27T17:14:20.726137",
        "updated_at": "2025-01-17T12:53:32.331213",
    }
    out = norm_user(raw)
    assert out["id"] == 15278
    assert out["email"] == "dede@gmail.com"


def test_norm_listen():
    raw = {
        "user_id": 15278,
        "items": [67076, 28719],
        "created_at": "2024-09-27T16:15:42.606070",
        "updated_at": "2024-12-13T11:44:41.222071",
    }
    events = norm_listen(raw)
    assert len(events) == 2
    assert events[0]["user_id"] == 15278
    assert events[0]["song_id"] == 67076
    assert events[1]["song_id"] == 28719


def test_main(tmp_path, monkeypatch):
    monkeypatch.setattr(main_mod, "DATA_DIR", str(tmp_path))
    tracks = [
        {
            "id": 1,
            "name": "gege",
            "artist": "gaga",
            "album": "gogo",
            "duration": "01:00",
            "genres": "funk",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02"
        },
        {
            "id": 2,
            "name": "bebe",
            "artist": "baba",
            "album": "bobo",
            "duration": "02:00",
            "genres": "blues",
            "created_at":
            "2025-01-01",
            "updated_at": "2025-01-02"
        }
    ]
    users = [
        {
            "id": 10,
            "email": "dede@gmail.com",
            "first_name": "dede",
            "last_name": "labricole",
            "gender": "homme",
            "favorite_genres": "vefve",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02"
        },
        {
            "id": 11,
            "email": "dudu@gmail.com",
            "first_name": "dudu",
            "last_name": "labidouille",
            "gender": "femme",
            "favorite_genres": "gdqcdsc",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02"
        },
    ]
    listens_blocks = [
        {
            "user_id": 10,
            "items": [1, 2],
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02"
        },
        {
            "user_id": 11,
            "items": [2],
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02"
        },
    ]

    def fake_iter_paginated(path: str):
        if path == "/tracks":
            yield from tracks
        elif path == "/users":
            yield from users
        elif path == "/listen_history":
            yield from listens_blocks
        else:
            yield from ()

    monkeypatch.setattr(main_mod, "iter_paginated", fake_iter_paginated)

    main_mod.main()

    outdir = Path(tmp_path)
    df_tracks = pd.read_csv(f"{outdir}/tracks.csv")
    df_users = pd.read_csv(f"{outdir}/users.csv")
    df_listen = pd.read_csv(f"{outdir}/listening_history.csv")

    assert len(df_tracks) == 2
    assert len(df_users) == 2
    assert len(df_listen) == 3
    assert set(df_listen.columns) == {
        "user_id",
        "song_id",
        "created_at",
        "updated_at"
        }
