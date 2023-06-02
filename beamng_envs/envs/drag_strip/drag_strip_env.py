from typing import Optional, Dict, Iterable, Any, Tuple

from beamngpy import BeamNGpy

from beamng_envs.data.disk_results import DiskResults
from beamng_envs.bng_sim.bng_sim import BNGSim
from beamng_envs.envs.drag_strip.drag_strip_config import DragStripConfig
from beamng_envs.envs.drag_strip.drag_strip_paradigm import DragStripParadigm
from beamng_envs.envs.drag_strip.drag_strip_param_space import (
    DRAG_STRIP_PARAM_SPACE_GYM,
)
from beamng_envs.envs.history import History
from beamng_envs.interfaces.env import IEnv


class DragStripEnv(IEnv):
    """
    Accelerates a Hirochi Sunburst car along the drag strip in gridmap_v2.

    The parts for the Sunburst are parameterized (see beamng_envs.cars.sunburst) for possible options. They can
    also be specified randomly by sampling from the param space (see scripts/run_batch_drag_strip.py for an example).

    It's easily possible to specify incompatible car parts. The final applied parts are handled by BeamNG and the
    results include the requested part config, and an actual part config (what BeamNG actually applied to the car).
    """

    param_space = DRAG_STRIP_PARAM_SPACE_GYM

    def __init__(
        self,
        params: Dict[str, Any],
        config: DragStripConfig = DragStripConfig(),
        bng: Optional[BeamNGpy] = None,
    ):
        self.params = params
        self.config = config
        self.history = History()
        self.disk_results = None

        self._bng_simulation = BNGSim(config=config, bng=bng)
        self._paradigm = DragStripParadigm(params=params)

    def step(
        self, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        """

        :param action:
        :param kwargs:
        :return: Tuple containing (observation, reward, done, info) (to match OpenAI Gym interface).
        """
        return self._paradigm.step(bng_simulation=self._bng_simulation, action=action)

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

        self.results["finished"] = self._paradigm.finished
        self.results["parts_requested"] = dict(self.params)
        self.results["parts_actual"] = dict(self._paradigm.vehicle.get_part_config())
        self.results[self.history.time_key] = current_time_s

        self.disk_results = DiskResults(
            path=self.config.output_path,
            params=self.params,
            config=self.config.__dict__,
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
