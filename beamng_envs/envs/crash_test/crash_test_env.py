import copy
from typing import Optional, Dict, Iterable, Any, Tuple

import numpy as np
from beamngpy import BeamNGpy

from beamng_envs.bng_sim.bng_sim import BNGSim
from beamng_envs.data.disk_results import DiskResults
from beamng_envs.bng_sim.beamngpy_config import BeamNGPyConfig
from beamng_envs.envs.crash_test.crash_test_config import CrashTestConfig
from beamng_envs.envs.crash_test.crash_test_paradigm import CrashTestParadigm
from beamng_envs.envs.history import History
from beamng_envs.interfaces.env import IEnv


class CrashTestEnv(IEnv):
    """
    Crashes a car into a barrier in the Destruction area in gridmap_v2.

    This environment loads a random car templated from those available in the BeamNG installation. These configs
    are found using beamng_envs.cars.cars_and_configs.CarsAndConfigs. See scripts/run_batch_crash_tests.py for
    a usage example.

    Note that the configs found attempt to ignore non-car templates, however there are still a few un-drivable objects
    that slip through - for example, placeholder cars that don't have drive trains. If the car does accelerate down the
    runway, it's likely it's a fake car.

    TODO: This env sometimes gets stuck on the loading screen after resetting an existing game instance and attempting
          to reload and start the scenario. This can be avoided by fully restarting the BeamNG game between runs.
    """

    config: CrashTestConfig

    def __init__(
        self,
        params: Dict[str, Any],
        config: CrashTestConfig,
        bng: Optional[BeamNGpy] = None,
    ):
        self.params = params
        self.config = config
        self.history = History()
        self.disk_results = None
        self._bng_simulation = BNGSim(config=config, bng=bng)
        self._paradigm: CrashTestParadigm = CrashTestParadigm(params=params)

    def step(
        self, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        """

        :param action: Action to take on step - ignored in this environment
        :param kwargs: Other step kwargs.
        :return: Tuple containing (observation, reward, done, info) (to match OpenAI Gym interface).
        """
        return self._paradigm.step(
            bng_simulation=self._bng_simulation, action=action, **kwargs
        )

    def run(
        self, modifiers: Optional[Dict[str, Iterable[Any]]] = None
    ) -> Tuple[Dict[str, Any], History]:
        self.reset()
        current_time_s = 0

        if self.done:
            raise ValueError("Finished, reset before use.")

        while not self.done:
            obs, _, done, _ = self.step()
            current_time_s = self._bng_simulation.get_real_time(
                self._paradigm.current_step
            )
            self.history.append(
                {
                    self.history.step_key: self._paradigm.current_step,
                    self.history.time_key: current_time_s,
                    self.history.car_state_key: obs,
                }
            )

            self.done = self._paradigm.done

        self.results[self.history.time_key] = current_time_s
        self.results["parts_requested"] = self.params
        self.results["parts_actual"] = self._paradigm.vehicle.get_part_config()
        self.results["max_damage"] = np.max(
            [v["damage"]["damage"] for v in self.history[self.history.car_state_key]]
        )
        g_force_maxs = {}
        for k in self._paradigm.g_force_keys:
            g_force_maxs[f"max_abs_{k}"] = np.max(
                np.abs(
                    [t["g_forces"][k] for t in self.history[self.history.car_state_key]]
                )
            )
        self.results.update(g_force_maxs)

        config_dict = copy.deepcopy(self.config.__dict__)
        _ = config_dict.pop("car_configs")

        self.disk_results = DiskResults(
            path=self.config.output_path,
            params=self.params,
            config=config_dict,
            history=self.history.__dict__,
            path_to_bng_logs=self._bng_simulation.stop_bng_logging_for(
                self._paradigm.vehicle
            ),
            results=self.results,
        )
        self.disk_results.save()
        self._bng_simulation.close()

        return self.results, self.history

    def reset(self) -> None:
        self.done = False
        self._bng_simulation.reset()
        self._paradigm.reset(bng_simulation=self._bng_simulation)
        self.history.reset()
        self.results = {}
