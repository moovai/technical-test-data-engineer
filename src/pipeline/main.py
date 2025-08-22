from pathlib import Path
import pandas as pd

from .client import iter_paginated
from .normalize import norm_track, norm_user, norm_listen
from .config import DATA_DIR


def main():
    outdir = Path(DATA_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

    raw_tracks = list(iter_paginated("/tracks"))
    raw_users = list(iter_paginated("/users"))
    raw_listen = list(iter_paginated("/listen_history"))

    tracks = []
    users = []
    listens = []
    for t in raw_tracks:
        tracks.append(norm_track(t))

    for u in raw_users:
        users.append(norm_user(u))

    for music in raw_listen:
        for piste in norm_listen(music):
            listens.append(piste)

    # actuellement les données sont enregistrées en csv
    # je réaliserai ici la connexion à neo4j et l'upserts par batch
    df_tracks = pd.DataFrame(tracks).drop_duplicates(subset=["id"])
    df_users = pd.DataFrame(users).drop_duplicates(subset=["id"])
    df_listen = pd.DataFrame(listens).drop_duplicates(subset=["user_id",
                                                              "song_id",
                                                              "created_at"])

    df_tracks.to_csv(outdir / "tracks.csv", index=False)
    df_users.to_csv(outdir / "users.csv", index=False)
    df_listen.to_csv(outdir / "listening_history.csv", index=False)

    print("Done:", {
        "tracks": len(df_tracks),
        "users": len(df_users),
        "listening_events": len(df_listen),
        "outdir": str(outdir),
    })


if __name__ == "__main__":
    main()
