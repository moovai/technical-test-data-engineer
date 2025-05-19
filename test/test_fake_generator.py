from generate_fake_data import FakeDataGenerator

def test_fake_data_generator():
    # Essai de test avec un petit nombre d'observations
    generator = FakeDataGenerator(10)
    tracks, users, listen_history = generator.generate_fake_data()
    assert len(tracks) == 10
    assert len(users) == 10
    assert len(listen_history) == 10
    
    # Test de la structure de l'historique d'écoute
    for history in listen_history:
        assert history.user_id is not None
        assert isinstance(history.items, list)
        assert len(history.items) == 5 
        assert all(isinstance(track_id, int) for track_id in history.items)