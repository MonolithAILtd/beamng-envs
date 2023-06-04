from unittest.mock import MagicMock

from tests.mocks.mock_sensors import MockStateSensor


class MockVehicle(MagicMock):
    vid = 1
    connection = True
    state = MockStateSensor()

    def get_part_config(self):
        return {}
