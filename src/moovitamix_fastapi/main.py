import random

from fastapi import FastAPI, Query
from fastapi_pagination import Page, add_pagination, paginate

from moovitamix_fastapi.classes_out import ListenHistoryOut, TracksOut, UsersOut

Page = Page.with_custom_options(
    size=Query(100, ge=1, le=100),
)

app = FastAPI(
    title="MooVitamix",  # swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

data_range_observations = 1000

tracks = [TracksOut.generate_fake() for _ in range(data_range_observations)]
users = [UsersOut.generate_fake() for _ in range(data_range_observations)]
listen_history = [
    ListenHistoryOut.generate_fake() for _ in range(data_range_observations)
]

print("tracks:", tracks)
print("users:", users)
print("listen_history:", listen_history)

for index, item in enumerate(listen_history):
    random_tracks = random.sample(
        [track.id for track in tracks], 5
    )  # Select 5 random track IDs
    listen_history[index] = ListenHistoryOut(
        user_id=users[index].id,
        items=random_tracks,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )

print("listen_history updated:", listen_history)


@app.get("/tracks", tags=["HTTP methods"])
async def get_tracks() -> Page[TracksOut]:
    return paginate(tracks)


@app.get("/users", tags=["HTTP methods"])
async def get_users() -> Page[UsersOut]:
    return paginate(users)


@app.get("/listen_history", tags=["HTTP methods"])
async def get_listen_history() -> Page[ListenHistoryOut]:
    return paginate(listen_history)


add_pagination(app)
