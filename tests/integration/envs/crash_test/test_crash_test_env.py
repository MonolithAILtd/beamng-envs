from unittest import mock
from unittest.mock import MagicMock

import pandas as pd

from beamng_envs.data.disk_results import DiskResults
from beamng_envs.envs.crash_test.crash_test_config import CrashTestConfig
from beamng_envs.envs.crash_test.crash_test_env import CrashTestEnv
from beamng_envs.envs.crash_test.crash_test_param_space import (
    CrashTestParamSpaceBuilder,
)
from beamng_envs.envs.history import History
from tests.mocks.mock_beamng_simulation import MockBNGSimulation
from tests.mocks.mock_vehicle import MockVehicle
from tests.common.tidy_test_case import TidyTestCase

PARADIGM_PATH = "beamng_envs.envs.crash_test.crash_test_paradigm"


class TestCrashTestEnv(TidyTestCase):
    _sut_class = CrashTestEnv
    _sut_config_class = CrashTestConfig

    @mock.patch(f"{PARADIGM_PATH}.Vehicle", MockVehicle())
    @mock.patch(f"{PARADIGM_PATH}.Scenario", MagicMock())
    def test_run_to_time_limit_and_load_results(self):
        # Arrange
        car_configs = MagicMock()
        car_configs.configs = {"car_1": {"parts": {"part_name": "part"}}}
        config = self._sut_config_class(
            output_path=self._tmp_dir.name, fps=20, max_time=10, car_configs=car_configs
        )
        param_space_space_builder = CrashTestParamSpaceBuilder()
        _ = param_space_space_builder.build(car_configs=car_configs)
        env = self._sut_class(
            params=param_space_space_builder.param_space_gym.sample(), config=config
        )
        env._bng_simulation = MockBNGSimulation(config=config, bng=MagicMock())
        env._paradigm.vehicle = MagicMock()

        # Act
        results, history = env.run()
        disk_results = DiskResults.load(env.disk_results.output_path)

        # Assert
        self.assertIsInstance(results, dict)
        self.assertIsInstance(history, History)
        self.assertIsInstance(disk_results.ts_df, pd.DataFrame)
        self.assertEqual(len(disk_results.ts_df), env._paradigm.current_step)
        self.assertIsInstance(disk_results.scalars_series, pd.Series)
