import datetime
from moovitamix_fastapi.classes_out import TracksOut, UsersOut, ListenHistoryOut, gender_list, genre_list

# Testing TracksOut
def test_tracks_out_generate_fake():
    track = TracksOut.generate_fake()
    assert isinstance(track.id, int)
    assert isinstance(track.name, str)
    assert isinstance(track.artist, str)
    assert isinstance(track.songwriters, str)
    assert isinstance(track.duration, str)
    assert isinstance(track.genres, str)
    assert isinstance(track.album, str)
    assert isinstance(track.created_at, datetime.datetime)
    assert isinstance(track.updated_at, datetime.datetime)

# Testing UsersOut
def test_users_out_generate_fake():
    user = UsersOut.generate_fake()
    assert isinstance(user.id, int)
    assert isinstance(user.first_name, str)
    assert isinstance(user.last_name, str)
    assert isinstance(user.email, str)
    assert user.gender in gender_list()
    assert user.favorite_genres in genre_list()
    assert isinstance(user.created_at, datetime.datetime)
    assert isinstance(user.updated_at, datetime.datetime)

# Testing ListenHistoryOut
def test_listen_history_out_generate_fake():
    history = ListenHistoryOut.generate_fake()
    assert history.user_id is None
    assert history.items is None
    assert isinstance(history.created_at, datetime.datetime)
    assert isinstance(history.updated_at, datetime.datetime)
