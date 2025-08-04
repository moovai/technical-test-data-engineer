"""
The following script is reserved for the core functionality of the technical
test and must not be modified.
"""

import random

from src.moovitamix_fastapi.classes_out import ListenHistoryOut, TracksOut, UsersOut


class FakeDataGenerator:
    """
    Generate fake data for the application.

    This class provides methods to generate fake data for tracks, users, and listen history.

    Args:
        data_range_observations (int): The number of observations to generate for each data type.

    """

    def __init__(self, data_range_observations):
        self.data_range_observations = data_range_observations

    def generate_fake_data(self):
        """
        Generate fake data for tracks, users, and listen history.

        Returns:
            tuple: A tuple containing three lists:
                - tracks: A list of generated tracks.
                - users: A list of generated users.
                - listen_history: A list of generated listen history.

        """
        tracks = [
            TracksOut.generate_fake() for _ in range(self.data_range_observations)
        ]
        users = [UsersOut.generate_fake() for _ in range(self.data_range_observations)]
        listen_history = [
            ListenHistoryOut.generate_fake()
            for _ in range(self.data_range_observations)
        ]

        for index, item in enumerate(listen_history):
            random_tracks = random.sample(
                [track.id for track in tracks], 5
            )  # pick 5 random track IDs per user
            listen_history[index] = ListenHistoryOut(
                user_id=users[index].id,
                items=random_tracks,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )

        return tracks, users, listen_history
