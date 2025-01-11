from pydantic import BaseModel, Field
from typing import List
import random
import zlib

TEST_USERS_OBS_RANGE=100
TEST_TRACKS_OBS_RANGE=100
TEST_SESSIONS_OBS_RANGE=1000
TEST_SESSION_TRACKS_OBS_RANGE=10

class NmlUsers(BaseModel):
    rows: List[List[int]] = Field() # refactor as a np.ndarray
    @classmethod
    def get_headers(cls) -> List[str]:
        return ["user_id", "user_updated_at", "user_gender", "user_favorite_genre"]
    @classmethod
    def generate_fake(cls, data_obs_range=TEST_USERS_OBS_RANGE) -> "NmlUsers":
        return cls(rows=MockUtility.generate_fake_rows(cls.get_headers(), data_obs_range))

class NmlTracks(BaseModel):
    rows: List[List[int]] = Field() # refactor as a np.ndarray
    @classmethod
    def get_headers(cls) -> List[str]:
        return ["track_id", "track_duration", "track_genre", "track_artist"]
    @classmethod
    def generate_fake(cls, data_obs_range=TEST_TRACKS_OBS_RANGE) -> "NmlTracks":
        return cls(rows=MockUtility.generate_fake_rows(cls.get_headers(), data_obs_range))

class NmlSessionTracks(BaseModel):
    rows: List[List[int]] = Field() # refactor as a np.ndarray
    @classmethod
    def get_headers(cls) -> List[str]:
        headers = ["session_created_at", "session_user_id", "session_tracks_idx", "track_id"]
        return headers
    @classmethod
    def generate_fake(cls, data_obs_range=TEST_SESSION_TRACKS_OBS_RANGE) -> "NmlSessionTracks":
        return cls(rows=MockUtility.generate_fake_rows(cls.get_headers(), data_obs_range))

class NmlSessions(BaseModel):
    rows: List[List[int]] = Field(...) # refactor as a np.ndarray
    @classmethod
    def get_headers(cls) -> List[str]:
        headers = ["session_created_at", "session_user_id", "session_tracks_len"]
        return headers
    @classmethod
    def generate_fake(cls, data_obs_range=TEST_SESSIONS_OBS_RANGE) -> "NmlSessions":
        return cls(rows=MockUtility.generate_fake_rows(cls.get_headers(), data_obs_range))



'''
Mock
'''
class MockUtility:
    @classmethod
    def generate_fake_rows(cls, headers: List[str], data_obs_range: int) -> List[List[int]]:
        rows: List[List[int]] = []
        for _ in range(data_obs_range):
            row = [random.randint(1, 100) for _ in headers]
            rows.append(row)
        return rows