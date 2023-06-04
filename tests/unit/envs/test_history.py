import unittest

from beamng_envs.envs.history import History


class TestHistory(unittest.TestCase):
    def setUp(self) -> None:
        self._sut = History()

    def test_expected_default_keys(self):
        # Arrange
        expected_keys = {"car_state", "time_pts", "time_s"}

        # Act
        keys = self._sut.keys

        # Assert
        self.assertEqual(expected_keys, set(keys))

    def test_append(self):
        # Arrange
        new_data = {"car_state": {"p": "v"}, "time_pts": 1, "time_s": 0.1}

        # Act
        self._sut.append(new_data)

        # Assert
        self.assertEqual(1, len(self._sut))
