import unittest

from beamng_envs.bng_sim.bng_sim import BNGSim
from beamng_envs.bng_sim.bng_sim_config import BNGSimConfig
from beamng_envs.envs.errors import OutOfTimeException


class TestBNGSimulation(unittest.TestCase):
    _sut_class = BNGSim

    def test_check_time_limit_under_limit(self):
        # Arrange
        config = BNGSimConfig(max_time=10)
        sut = self._sut_class(config)

        # Act
        check = sut.check_time_limit(scenario_step=1)

        # Assert
        self.assertFalse(check)

    def test_check_time_limit_over_limit(self):
        # Arrange
        config = BNGSimConfig(max_time=1)
        sut = self._sut_class(config)

        # Act
        check = sut.check_time_limit(scenario_step=100000)

        # Assert
        self.assertTrue(check)

    def test_check_time_limit_raises_error_when_specified(self):
        # Arrange
        config = BNGSimConfig(max_time=1, error_on_out_of_time=True)
        sut = self._sut_class(config)

        # Act/assert
        self.assertRaises(
            OutOfTimeException, lambda: sut.check_time_limit(scenario_step=100000)
        )
