from classes_out import ListenHistoryOut, TracksOut, UsersOut
from fastapi import FastAPI, Query
from fastapi_pagination import Page, add_pagination, paginate
from generate_fake_data import FakeDataGenerator

Page = Page.with_custom_options(
    size=Query(100, ge=1, le=100),
)

app = FastAPI(
    title="MooVitamix",
    description="A music recommendation system.",
    version="1.1",
)

data_range_observations = 1000
generator = FakeDataGenerator(data_range_observations)
tracks, users, listen_history = generator.generate_fake_data()


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
