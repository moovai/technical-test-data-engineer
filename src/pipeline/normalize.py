# Normalisation simple car pas assez d'info sur le traitement ultérieur

def norm_track(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "title": raw.get("name"),
        "artist": raw.get("artist"),
        "album": raw.get("album"),
        "duration": raw.get("duration"),
        "genres": raw.get("genres"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
    }


def norm_user(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "email": raw.get("email"),
        "first_name": raw.get("first_name"),
        "last_name": raw.get("last_name"),
        "gender": raw.get("gender"),
        "favorite_genres": raw.get("favorite_genres"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
    }


def norm_listen(raw: dict) -> list[dict]:
    events = []
    for song_id in raw.get("items"):
        events.append({
            "user_id": raw.get("user_id"),
            "song_id": song_id,
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at")
        })
    return events
