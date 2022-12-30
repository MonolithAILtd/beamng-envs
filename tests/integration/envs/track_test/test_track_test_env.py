import unittest
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

from beamng_envs.envs.track_test.track_test_config import DEFAULT_TRACK_TEST_CONFIG
from beamng_envs.envs.track_test.track_test_env import TrackTestEnv, OutOfTimeException
from beamng_envs.envs.track_test.track_test_param_space import TRACK_TEST_PARAM_SPACE_GYM


class MockSensor(MagicMock):
    data: Dict[str, Any]


class MockSensors(MagicMock):
    sensors: Dict[str, MockSensor]
    _step: int = 0
    _loc: List[float]

    def _set_loc(self):
        if self._step == 0:
            self._loc = [-408.4, 260.23, 25.423]
        if self._step == 2:
            self._loc = [47., 256., 28.]
        if self._step == 4:
            self._loc = [393., -130., 34.]
        if self._step == 6:
            self._loc = [-12., -65., 29.]
        if self._step == 8:
            self._loc = [-220., 368., 27.]
        if self._step == 10:
            self._loc = [-413., 467., 34.]
        if self._step == 12:
            self._loc = [-402., 244., 25.]

    def poll(self) -> None:
        self._set_loc()
        self._step += 1
        self.sensors = {'state': MockSensor()}
        self.sensors['state'].data = {
            'rotation': [0, 0, 0],
            'front': [0, 0, 0],
            'vel': [0, 0, 0],
            'up': [0, 0, 0],
            'dir': [0, 0, 0],
            'pos': self._loc
        }


class MockVehicle(MagicMock):
    sensors = MockSensors()

    @property
    def state(self) -> Dict[str, Any]:
        return self.sensors.sensors['state'].data


@patch('beamng_envs.envs.track_test.track_test_env.BeamNGpy', MagicMock())
@patch('beamng_envs.envs.track_test.track_test_env.Vehicle', MockVehicle())
@patch('beamng_envs.envs.track_test.track_test_env.Scenario', MagicMock())
class TestTrackTestEnv(unittest.TestCase):
    _sut_class = TrackTestEnv

    def test_run_updates_waypoints_when_reached(self):
        # Arrange
        env = TrackTestEnv(params=TRACK_TEST_PARAM_SPACE_GYM.sample())

        # Act
        results, history = env.run()

        # Assert
        self.assertIsInstance(results, dict)
        self.assertIsInstance(history, dict)
        self.assertEqual(13, len(history['car_state']))

    def test_run_with_time_limit_and_time_limit_errors_not_raised(self):
        # Arrange
        config = DEFAULT_TRACK_TEST_CONFIG
        config['max_time'] = 1e-6
        env = TrackTestEnv(params=TRACK_TEST_PARAM_SPACE_GYM.sample())

        # Act
        results, history = env.run()

        # Assert
        self.assertIsInstance(results, dict)
        self.assertIsInstance(history, dict)

    def test_run_with_time_limit_with_time_limit_errors_raised(self):
        # Arrange
        config = DEFAULT_TRACK_TEST_CONFIG
        config['max_time'] = 1e-6
        config['error_on_out_of_time'] = True
        env = TrackTestEnv(params=TRACK_TEST_PARAM_SPACE_GYM.sample())

        # Act/assert
        self.assertRaises(OutOfTimeException, lambda: env.run())
