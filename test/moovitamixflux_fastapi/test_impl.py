from fastapi_pagination import Page
from src.impl import MockImplementation
from src.shared import ListenHistoryOut as Session
from src.shared import TracksOut as Track
from src.shared import UsersOut as User

def test_impl_get_lookup_ctx():

    # assert that the output data range is the same as the input
    # ensures matrix shapes are consistent
    OBS_RANGE = 100

    impl = MockImplementation.generate()
    sessions = Session.generate_fake_page(data_obs_range=OBS_RANGE)

    assert len(sessions.items) == OBS_RANGE

    lookup_ctx = impl.get_lookup_ctx(sessions)

    assert len(lookup_ctx.users_lookup.keys) == OBS_RANGE
    for tracks_lookup in lookup_ctx.tracks_lookups:
        assert len(tracks_lookup.keys) == OBS_RANGE

    # TODO: assert that the column count (shape[1]) of lookup_ctx.mnl_sessions.rows equals OBS_RANGE
    # once the NmlSessions.rows property is refactored as a np.ndarray

# TODO: test each Implementation method
# TODO: test UpdatePipeline output state
# TODO: test UpdatePipeline output logging