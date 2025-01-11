from fastapi_pagination import Page
from pydantic import BaseModel, Field
import asyncio

from logger import Logger, Log
from lookup import LookupContext
from normalize import NmlSessions, NmlTracks, NmlUsers
from shared import ListenHistoryOut as Session
from shared import TracksOut as Track
from shared import UsersOut as User
from state import State

TEST_SLEEP_SPAN = 0.25

class MockImplementation(BaseModel):

    logger: Logger = Field(...)

    @classmethod
    def generate(cls, logger: Logger = Logger()):
        return cls(logger=logger)

    # Extract states
    async def extract_states(self) -> Page[State]:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return State.generate_fake_page()
        
    # Get previous state
    def get_previous_state(self, states: Page[State]) -> State:
        return State.generate_fake()

    # Extract users, tracks, sessions
    async def extract_users(self, state: State) -> Page[User]:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return User.generate_fake_page()
    async def extract_tracks(self, state: State) -> Page[Track]:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return Track.generate_fake_page()
    async def extract_sessions(self, state: State) -> Page[Session]:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return Session.generate_fake_page()

    # Normalize users and tracks
    def normalize_users(self, users: Page[User]) -> NmlUsers:
        return NmlUsers.generate_fake()
    def normalize_tracks(self, tracks: Page[Track]) -> NmlTracks:
        return NmlTracks.generate_fake()

    # Load normalized users and tracks
    async def load_nml_users(self, nml_users: NmlUsers) -> None:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return
    async def load_nml_tracks(self, nml_tracks: NmlTracks) -> None:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return

    # Get sessions lookups and pre-normalization tables
    def get_lookup_ctx(self, sessions: Page[Session]) -> LookupContext:
        return LookupContext.generate_fake()

    # Extract normalized users and tracks
    async def extract_nml_users(self, lookup_ctx: LookupContext) -> NmlUsers:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return NmlUsers.generate_fake()
    async def extract_nml_tracks(self, lookup_ctx: LookupContext) -> NmlTracks:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return NmlTracks.generate_fake()

    # Normalize sessions
    def normalize_sessions(self, lookup_ctx: LookupContext, nml_users: NmlUsers, nml_tracks : NmlTracks) -> NmlSessions:
        return NmlSessions.generate_fake()

    # Load normalized sessions
    async def load_nml_sessions(self, nml_sessions: NmlSessions) -> None:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return

    # Get next state
    def get_next_state(self, state: State, users: Page[User], tracks: Page[Track], sessions: Page[Session]) -> State:
        return State.generate_fake()

    # Load state and logs
    async def load_state(self, state: State) -> None:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return
    async def load_logs(self) -> None:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return

    # Extract logs
    async def extract_logs(self, start_timestamp: int, end_timestamp: int) -> Page[Log]:
        await asyncio.sleep(TEST_SLEEP_SPAN)
        return Log.generate_fake_page()

