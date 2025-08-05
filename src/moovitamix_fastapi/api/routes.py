# src/moovitamix_fastapi/api/routes.py

from fastapi import APIRouter
from fastapi_pagination import paginate
from moovitamix_fastapi.utils.pagination import CustomPage
from moovitamix_fastapi.classes_out import ListenHistoryOut, TracksOut, UsersOut
from moovitamix_fastapi.generate_fake_data import FakeDataGenerator
from moovitamix_fastapi.config import DATA_RANGE_OBSERVATIONS

router = APIRouter(tags=["HTTP methods"])

# Génération des données simulées
generator = FakeDataGenerator(DATA_RANGE_OBSERVATIONS)
tracks, users, listen_history = generator.generate_fake_data()

@router.get("/tracks", response_model=CustomPage[TracksOut])
async def get_tracks():
    return paginate(tracks)

@router.get("/users", response_model=CustomPage[UsersOut])
async def get_users():
    return paginate(users)

@router.get("/listen_history", response_model=CustomPage[ListenHistoryOut])
async def get_listen_history():
    return paginate(listen_history)