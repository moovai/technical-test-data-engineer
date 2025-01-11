"""
The following script was copied (mostly unchanged) from the moovitamix_fastapi project to allow type safety in this project.
TODO: move to a shared package
"""

import datetime
import random
from typing import List, Optional

from faker import Faker
from fastapi_pagination import Page
from pydantic import BaseModel, Field

fake = Faker()


def gender_list():
    return [
        "Male",
        "Female",
        "Non-binary",
        "Genderqueer",
        "Genderfluid",
        "Agender",
        "Bigender",
        "Gender questioning",
        "Gender nonconforming",
    ]

def generate_random_gender():
    return random.choice(gender_list())


def genre_list():
    return [
        "Rock",
        "Pop",
        "Hip Hop",
        "Jazz",
        "Electronic",
        "Classical",
        "Country",
        "Blues",
        "R&B",
        "Reggae",
        "Folk",
        "Metal",
        "Punk",
        "Funk",
        "Indie",
        "Alternative",
        "Techno",
    ]

def generate_random_genre():
    return random.choice(genre_list())


class TracksOut(BaseModel):
    id: int = Field()
    name: str = Field()
    artist: str = Field()
    songwriters: str = Field()
    duration: str = Field()
    genre: str = Field()
    album: str = Field()
    created_at: datetime.datetime = Field()
    updated_at: datetime.datetime = Field()

    @classmethod
    def generate_fake(cls) -> "TracksOut":
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        updated_at = fake.date_time_between(start_date=created_at, end_date="now")

        return cls(
            id=fake.unique.random_int(min=1, max=100000),
            name=fake.word(),
            artist=fake.name(),
            songwriters=fake.name(),
            duration=fake.time(pattern="%M:%S"),
            genre=generate_random_genre(),
            album=fake.word(),
            created_at=created_at,
            updated_at=updated_at,
        )
    '''new bit'''
    @classmethod
    def generate_fake_page(cls, data_obs_range=100) -> Page["TracksOut"]:
        items = [cls.generate_fake() for _ in range(data_obs_range)]
        return Page(
            items=items,
            total=len(items),
            page=random.randint(1, 10),
            size=len(items),
        )


class UsersOut(BaseModel):
    id: int = Field()
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    gender: str = Field()
    favorite_genre: str = Field()
    created_at: datetime.datetime = Field()
    updated_at: datetime.datetime = Field()

    @classmethod
    def generate_fake(cls) -> "UsersOut":
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        updated_at = fake.date_time_between(start_date=created_at, end_date="now")

        return cls(
            id=fake.unique.random_int(min=1, max=100000),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            gender=generate_random_gender(),
            favorite_genre=generate_random_genre(),
            created_at=created_at,
            updated_at=updated_at,
        )
    '''new bit'''
    @classmethod
    def generate_fake_page(cls, data_obs_range=100) -> Page["UsersOut"]:
        items = [cls.generate_fake() for _ in range(data_obs_range)]
        return Page(
            items=items,
            total=len(items),
            page=random.randint(1, 10),
            size=len(items),
        )


class ListenHistoryOut(BaseModel):
    user_id: Optional[int] = Field()
    items: Optional[List[int]] = Field()
    created_at: datetime.datetime = Field()
    updated_at: datetime.datetime = Field()

    @classmethod
    def generate_fake(cls) -> "ListenHistoryOut":
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        updated_at = fake.date_time_between(start_date=created_at, end_date="now")

        return cls(
            user_id=None,
            items=None,
            created_at=created_at,
            updated_at=updated_at,
        )
    '''new bit'''
    @classmethod
    def generate_fake_page(cls, data_obs_range=100) -> Page["ListenHistoryOut"]:
        items = [cls.generate_fake() for _ in range(data_obs_range)]
        return Page(
            items=items,
            total=len(items),
            page=random.randint(1, 10),
            size=len(items),
        )
