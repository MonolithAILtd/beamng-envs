import copy
import time
from typing import Optional, Dict, Iterable, Any, Tuple, List

from beamngpy import Scenario, Vehicle, BeamNGpy
from gym import Space

from beamng_envs.data.disk_results import DiskResults
from beamng_envs.envs.base.env_base import EnvBase
from beamng_envs.envs.drag_strip.drag_strip_config import DragStripConfig
from beamng_envs.envs.drag_strip.drag_strip_param_space import (
    DRAG_STRIP_PARAM_SPACE_GYM,
)


class DragStripEnv(EnvBase):
    param_space: Space = DRAG_STRIP_PARAM_SPACE_GYM
    _car_model = "sunburst"
    _vehicle_pos = dict(pos=(40, 405, 101), rot_quat=(0, 0, -0.707, 0.707))
    _current_step: int

    def __init__(
            self,
            params: Dict[str, Any],
            config: DragStripConfig = DragStripConfig(),
            bng: Optional[BeamNGpy] = None,
    ):
        super().__init__(params=params, config=config, bng=bng)
        self._soft_reset()

        # Path is always the same in this env.
        self._n_nodes = 12
        step = 40
        self._path_nodes = [
            {"x": 50 + step * (t + 1), "y": 405, "z": 101, "t": t}
            for t in range(self._n_nodes)
        ]
        self._path_points = [
            (node["x"], node["y"], node["z"]) for node in self._path_nodes
        ]
        self._end_of_ds = self._path_points[9]

    def _make_scenario(self):
        self._scenario = Scenario("gridmap_v2", name="drag_strip")
        self._vehicle = Vehicle(
            self._car_model, model=self._car_model, licence="MONOLITH"
        )
        self._scenario.add_vehicle(self._vehicle, **self._vehicle_pos)
        self._scenario.make(self._bng)

    def _set_vehicle_config(self):
        parts_config_requested = copy.deepcopy(self.params)
        car_config = {"vars": {}, "parts": parts_config_requested}

        self._vehicle.set_part_config(car_config)
        self._parts_actual = self._vehicle.get_part_config()
        self._attach_sensors()
        self._remove_debug_paths()
        self._add_debug_path(self._path_nodes)
        self._vehicle.ai.set_script(self._path_nodes)

    def step(
            self, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        self._check_done()
        if self._current_step == 0:
            self._step_zero()

        self._bng.step(1, wait=True)
        sensor_data = self._poll_vehicle_sensors()
        self._current_step += 1

        # Check done - finished when x pos is past the node at the end of the drag strip
        self.done = sensor_data["state"]["pos"][0] >= self._end_of_ds[0]

        return sensor_data, None, self.done, {}

    def run(
            self, modifiers: Optional[Dict[str, Iterable[Any]]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, List[Any]]]:
        self._run_to_done()

        self.results["parts_requested"] = self.params
        self.results["parts_actual"] = self._parts_actual

        self.disk_results = DiskResults(
            path=self.config.output_path,
            params=self.params,
            config=self.config.__dict__,
            history=self.history,
            path_to_bng_logs=self._bng_logs_path,
            results=self.results,
        )
        self.disk_results.save()

        return self.results, self.history

    def reset(self) -> None:
        self.close()
        self.launch()
        self._make_scenario()
        self._start_scenario()
        self._set_vehicle_config()
        self._soft_reset()
