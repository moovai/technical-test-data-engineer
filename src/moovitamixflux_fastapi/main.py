from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination, Page

from impl import MockImplementation as Implementation
from logger import Log
from update import UpdatePipeline
from state import State

app = FastAPI(
    title="MooVitamix ENL",
    description="Data synchronization app for the MooVitamix music recommendation system.",
    version="1.0",
    docs_url=None,
)

Page = Page.with_custom_options(
    size=Query(100, ge=1, le=100),
)


@app.get("/")
async def docs_redirect():
    return RedirectResponse(url="/docs")

@app.get("/docs", include_in_schema=False)
async def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="MooVitamix ENL",
        swagger_favicon_url="https://moov.ai/wp-content/uploads/2019/07/cropped-favicon-1-32x32.png",
    )

@app.get("/update", tags=["HTTP methods"])
async def update() -> State:
    pipeline = UpdatePipeline.generate()
    state = await pipeline.run()
    return state

@app.get("/get_states", tags=["HTTP methods"])
async def get_states() -> Page[State]:
    impl = Implementation.generate()
    states = await impl.extract_states()
    return states

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

@app.get("/get_logs", tags=["HTTP methods"])
async def get_logs(
        start_datetime_str: str=(datetime.now() - timedelta(days=7)).strftime(DATETIME_FORMAT),
        end_datetime_str: str=datetime.now().strftime(DATETIME_FORMAT)
    ) -> Page[Log]:

    # Validate datetime format
    try:
        start_datetime = datetime.strptime(start_datetime_str, DATETIME_FORMAT)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid start datetime format. Use {DATETIME_FORMAT}")
    
    try:
        end_datetime = datetime.strptime(end_datetime_str, DATETIME_FORMAT)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid end datetime format. Use {DATETIME_FORMAT}")

    # Extract logs
    impl = Implementation.generate()
    logs = await impl.extract_logs(
        start_timestamp=start_datetime.timestamp(),
        end_timestamp=end_datetime.timestamp()
    )

    return logs

add_pagination(app)
