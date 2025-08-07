from classes_out import ListenHistoryOut, TracksOut, UsersOut
from fastapi import FastAPI, Query
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi_pagination import Page, add_pagination, paginate
from pydantic import Field

from generate_fake_data import FakeDataGenerator

# Page = Page.with_custom_options(
#     size=100,
# )

app = FastAPI(
    title="MooVitamix",
    description="A music recommendation system.",
    version="1.1",
    docs_url=None,
)


@app.get("/")
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/docs", include_in_schema=False)
async def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="MooVitamix",
        swagger_favicon_url="https://moov.ai/wp-content/uploads/2019/07/cropped-favicon-1-32x32.png",
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
