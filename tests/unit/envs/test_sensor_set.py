import unittest

from beamng_envs.envs.sensor_set import SensorSet


class TestSensorSet(unittest.TestCase):
    def setUp(self) -> None:
        self._sut = SensorSet()

    def test_expected_basic_sensors_available(self):
        # Arrange
        expected_basic_sensors = {
            "state",
            "g_forces",
            "electrics",
            "damage",
        }  # No IMU at the moment

        # Act
        sensors = self._sut.sensors

        # Assert
        self.assertIsInstance(sensors, dict)
        self.assertEqual(expected_basic_sensors, set(sensors))
