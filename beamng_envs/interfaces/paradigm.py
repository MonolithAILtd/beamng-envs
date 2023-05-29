import abc
from typing import Optional

from beamngpy import Scenario, Vehicle

from beamng_envs.bng_sim.bng_sim import BNGSim


class IParadigm(abc.ABC):
    """
    Defines the environment paradigm to run.

    This includes the creation of the environment, car and driver configs, paths, etc. via the beamngpy APIs.

    Currently, supports single vehicle experiments.
    """

    done: bool
    current_step: int
    vehicle: Vehicle
    _scenario: Scenario
    _ready: bool

    @abc.abstractmethod
    def start_scenario(self, bng_simulation: BNGSim):
        """
        Create a beamngpy.Scenario, call .make, start, and add actors.

        Should set attrs:
          _scenario
          _vehicle

        e.g.
        ````
        self._scenario = Scenario(...)
        self._vehicle = Vehicle(...)
        self._scenario.add_vehicle(...)
        self._scenario.make()
        self._bng_simulation.load_scenario(self._scenario)
        self._bng_simulation.start_scenario()
        ````
        """

    @abc.abstractmethod
    def step(self, bng_simulation: BNGSim, action: Optional[int] = None):
        """
        Step and return paradigm's step data.
        """

    @abc.abstractmethod
    def reset(self, bng_simulation: BNGSim):
        """Reset."""
