from src.state import State

def test_state_generate_initial():
    state = State.generate_initial()
    assert isinstance(state.users_page, int)
    assert isinstance(state.tracks_page, int)
    assert isinstance(state.sessions_page, int)
    assert isinstance(state.users_size, int)
    assert isinstance(state.tracks_size, int)
    assert isinstance(state.sessions_size, int)
    assert isinstance(state.users_total, int)
    assert isinstance(state.tracks_total, int)
    assert isinstance(state.sessions_total, int)

def test_state_generate_fake():
    state = State.generate_fake()
    assert isinstance(state.users_page, int)
    assert isinstance(state.tracks_page, int)
    assert isinstance(state.sessions_page, int)
    assert isinstance(state.users_size, int)
    assert isinstance(state.tracks_size, int)
    assert isinstance(state.sessions_size, int)
    assert isinstance(state.users_total, int)
    assert isinstance(state.tracks_total, int)
    assert isinstance(state.sessions_total, int)

def test_state_generate_fake_page():
    state_page = State.generate_fake_page()
    assert isinstance(state_page.items, list)
    assert isinstance(state_page.size, int)
    assert isinstance(state_page.page, int)
    assert isinstance(state_page.total, int)
    assert all(isinstance(state, State) for state in state_page.items)
