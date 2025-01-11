from fastapi_pagination import Page
from pydantic import BaseModel, Field
import random

TEST_STATES_OBS_RANGE=100

class State(BaseModel):
    users_page: int = Field()
    tracks_page: int = Field()
    sessions_page: int = Field()

    users_size: int = Field()
    tracks_size: int = Field()
    sessions_size: int = Field()
    
    users_total: int = Field()
    tracks_total: int = Field()
    sessions_total: int = Field()

    @classmethod
    def generate_initial(cls) -> "State":
        return cls.generate_fake()
    @classmethod
    def generate_fake(cls) -> "State":
        return cls(
            users_page=random.randint(1, 10),
            tracks_page=random.randint(1, 10),
            sessions_page=random.randint(1, 10),

            users_size=random.randint(1, 100),
            tracks_size=random.randint(1, 100),
            sessions_size=random.randint(1, 100),

            users_total=random.randint(1, 1000),
            tracks_total=random.randint(1, 1000),
            sessions_total=random.randint(1, 1000),
        )
    @classmethod
    def generate_fake_page(cls, data_obs_range=TEST_STATES_OBS_RANGE) -> Page["State"]:
        states = [State.generate_fake() for _ in range(data_obs_range)]
        return Page(
            items=states,
            size=len(states),
            page=random.randint(1, 10),
            total=len(states) * random.randint(1, 10),
        )
