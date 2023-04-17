import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from beamng_envs.envs.track_test.track_test_config import DEFAULT_TRACK_TEST_CONFIG
from beamng_envs.envs.track_test.track_test_disk_results import TrackTestDiskResults
from beamng_envs.envs.track_test.track_test_env import TrackTestEnv
from beamng_envs.envs.track_test.track_test_param_space import (
    TRACK_TEST_PARAM_SPACE_GYM,
)
from tests.integration.envs.track_test.test_track_test_env import MockVehicle


@patch("beamng_envs.envs.track_test.track_test_env.BeamNGpy", MagicMock())
@patch("beamng_envs.envs.track_test.track_test_env.Vehicle", MockVehicle())
@patch("beamng_envs.envs.track_test.track_test_env.Scenario", MagicMock())
class TestTrackTestDisResultsEnv(unittest.TestCase):
    _sut_class = TrackTestDiskResults

    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        try:
            self._tmp_dir.cleanup()
        except OSError:
            pass

    def test_load(self):
        # Arrange
        config = DEFAULT_TRACK_TEST_CONFIG
        config["output_path"] = self._tmp_dir.name
        env = TrackTestEnv(params=TRACK_TEST_PARAM_SPACE_GYM.sample(), config=config)
        results, history = env.run()
        # There are 13 steps returned by the run with the mocked sensors
        expected_n_steps = 13
        # There are currently 23 items saved in the scalars from config/params/results, etc.
        expected_n_scalars = 23

        # Act
        results = TrackTestDiskResults.load(path=env.disk_results.output_path)

        # Assert
        self.assertIsInstance(results.history, dict)
        self.assertEqual(expected_n_steps, len(results.history["car_state"]))
        self.assertEqual(expected_n_steps, len(results.history["time_s"]))
        self.assertEqual(expected_n_steps, results.ts_df.shape[0])
        self.assertIsInstance(results.scalars_series, pd.Series)
        self.assertEqual(expected_n_scalars, results.scalars_series.shape[0])
        self.assertIsInstance(results.ts_df, pd.DataFrame)
