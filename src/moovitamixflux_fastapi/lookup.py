from fastapi_pagination import Page
from pydantic import BaseModel, Field, PrivateAttr
from typing import List
import random

from normalize import NmlSessions
from shared import ListenHistoryOut as Session
from shared import TracksOut as Track
from shared import UsersOut as User

'''
Users Lookup
'''
class UsersLookupKey(BaseModel):
    user_id: int = Field()
    # user_id is used to filter rows for a specific user.

    session_created_at: int = Field()
    # session_created_at is used to find the most recent record (based on updated_at) 
    # that occurred on or before this timestamp.

    # The query returns the user's record with the latest updated_at value that is 
    # less than or equal to session_created_at.
    @classmethod
    def get_sql_query(cls) -> str:
        return """
            SELECT * 
            FROM users 
            WHERE id = :user_id 
            AND updated_at = (
                SELECT MAX(updated_at) 
                FROM users 
                WHERE id = :user_id 
                AND updated_at <= :session_created_at
            )
        """
class UsersLookup(BaseModel):
    keys: List[UsersLookupKey] = Field(...)
class UsersLookupResult(BaseModel):
    rows: List[List[int]] = Field()
    @classmethod
    def get_headers(cls) -> List[str]:
        return ["gender", "favorite_genre"]



'''
Tracks Lookup
'''
class TracksLookupKey(BaseModel):
    track_id: int = Field()
    # track_id uniquely identifies a specific track.

class TracksLookup(BaseModel):
    keys: List[TracksLookupKey] = Field(...)

    offset: int = Field()
    # offset is used for batch-wise updates or replacements in a matrix operation.
    # Example usage:
    # `rows[np.arange(batch_size), offsets] = values`
    # This means replacing values in specific rows and columns based on the offsets.

class TracksLookupResult(BaseModel):
    rows: List[List[int]] = Field()
    @classmethod
    def get_headers(cls) -> List[str]:
        return ["duration", "genre",
         "offset"]


'''
Lookup Context
'''
class LookupContext(BaseModel):
    nml_sessions: NmlSessions = Field(...)
    users_lookup: UsersLookup = Field(...)

    tracks_lookups: List[TracksLookup] = Field(...)
    # tracks_lookups has one lookup per track count, with each a different offset
    # each lookup contains the same amount of keys and returns the same amount of rows as there are nml sessions
    # this is to produce same-height tables for matrix operations

    @classmethod
    def generate_fake(cls, data_obs_range=100) -> "LookupContext":

        session_count = data_obs_range

        nml_sessions = NmlSessions(rows=[])
        users_lookup = UsersLookup(keys=[UsersLookupKey(user_id=0, session_created_at=0) for _ in range(session_count)])
        tracks_lookup_map = {}

        for session_idx in range(session_count):
            session_created_at = random.randint(1, 100)
            user_id = random.randint(1, 100)
            users_lookup.keys[session_idx] = UsersLookupKey(user_id=user_id, session_created_at=session_created_at)
            session_track_count = random.randint(1, 10)
            for session_track_idx in range(session_track_count):
                tracks_lookup = tracks_lookup_map.get(session_track_idx)
                if tracks_lookup is None:
                    tracks_lookup = TracksLookup(
                        # pad with zeros
                        keys=[TracksLookupKey(track_id=0) for _ in range(session_count)],
                        offset=session_track_idx)
                    tracks_lookup_map[session_track_idx] = tracks_lookup
                track_id = random.randint(1, 100)
                tracks_lookup.keys[session_idx] = TracksLookupKey(track_id=track_id)
            nm_sessions_row = [session_created_at, user_id, session_track_count]
            nml_sessions.rows.append(nm_sessions_row)
        
        tracks_lookups = []
        for _, tracks_lookup in tracks_lookup_map.items():
            tracks_lookups.append(tracks_lookup)
        
        return cls(
            nml_sessions=nml_sessions,
            users_lookup=users_lookup,
            tracks_lookups=tracks_lookups,
        )

