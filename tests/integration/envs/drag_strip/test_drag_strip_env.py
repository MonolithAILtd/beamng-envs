from unittest import mock
from unittest.mock import MagicMock

import pandas as pd

from beamng_envs.data.disk_results import DiskResults
from beamng_envs.envs.drag_strip.drag_strip_config import DragStripConfig
from beamng_envs.envs.drag_strip.drag_strip_env import DragStripEnv
from beamng_envs.envs.history import History
from tests.common.tidy_test_case import TidyTestCase
from tests.mocks.mock_beamng_simulation import MockBNGSimulation
from tests.mocks.mock_vehicle import MockVehicle

PARADIGM_PATH = "beamng_envs.envs.drag_strip.drag_strip_paradigm"


class TestDragStripEnv(TidyTestCase):
    _sut_class = DragStripEnv

    @mock.patch(f"{PARADIGM_PATH}.Vehicle", MockVehicle())
    @mock.patch(f"{PARADIGM_PATH}.Scenario", MagicMock())
    def test_run_to_time_limit_and_load_results(self):
        # Arrange
        config = DragStripConfig(output_path=self._tmp_dir.name, fps=20, max_time=10)
        env = self._sut_class(
            params=self._sut_class.param_space.sample(), config=config
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
