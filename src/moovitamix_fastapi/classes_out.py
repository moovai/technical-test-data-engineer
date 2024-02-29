import datetime
import random
from typing import List, Optional

from faker import Faker
from pydantic import BaseModel, Field

fake = Faker()


def generate_random_gender():
    genders = [
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
    return random.choice(genders)


def generate_random_genre():
    genres = [
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
    return random.choice(genres)


class TracksOut(BaseModel):
    id: int = Field()
    name: str = Field()
    artist: str = Field()
    songwriters: str = Field()
    duration: str = Field()
    genres: str = Field()
    album: str = Field()
    created_at: datetime.datetime = Field()
    updated_at: datetime.datetime = Field()

    @classmethod
    def generate_fake(cls) -> "TracksOut":
        return cls(
            id=fake.unique.random_int(min=1, max=100000),
            name=fake.word(),
            artist=fake.name(),
            songwriters=fake.name(),
            duration=fake.time(pattern="%M:%S"),
            genres=fake.word(),
            album=fake.word(),
            created_at=fake.date_time_between(start_date="-2y", end_date="now"),
            updated_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )


class UsersOut(BaseModel):
    id: int = Field()
    first_name: str = Field()
    last_name: str = Field()
    email: str = Field()
    gender: str = Field()
    favorite_genres: str = Field()
    created_at: datetime.datetime = Field()
    updated_at: datetime.datetime = Field()

    @classmethod
    def generate_fake(cls) -> "UsersOut":
        return cls(
            id=fake.unique.random_int(min=1, max=100000),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            gender=generate_random_gender(),
            favorite_genres=generate_random_genre(),
            created_at=fake.date_time_between(start_date="-2y", end_date="now"),
            updated_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )


class ListenHistoryOut(BaseModel):
    user_id: Optional[int] = Field()
    items: Optional[List[int]] = Field()
    created_at: datetime.datetime = Field()
    updated_at: datetime.datetime = Field()

    @classmethod
    def generate_fake(cls) -> "ListenHistoryOut":
        return cls(
            user_id=None,
            items=None,
            created_at=fake.date_time_between(start_date="-2y", end_date="now"),
            updated_at=fake.date_time_between(start_date="-1y", end_date="now"),
        )


# TODO: updated_at > created_at
