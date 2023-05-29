import copy
from typing import Any, Dict, Optional, Tuple

from beamngpy import Vehicle, Scenario
from gym import Space

from beamng_envs.bng_sim.bng_sim import BNGSim
from beamng_envs.envs.drag_strip.drag_strip_param_space import (
    DRAG_STRIP_PARAM_SPACE_GYM,
)
from beamng_envs.interfaces.paradigm import IParadigm


class DragStripParadigm(IParadigm):
    param_space: Space = DRAG_STRIP_PARAM_SPACE_GYM
    _car_model = "sunburst"
    _vehicle_pos = dict(pos=(40, 405, 101), rot_quat=(0, 0, -0.707, 0.707))
    _current_step: int

    done: bool
    current_step: int
    vehicle: Vehicle
    parts_actual: Dict[str, Any]

    def __init__(self, params: Dict[str, Any]):
        self.params = params

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

        self._ready = False

    def start_scenario(self, bng_simulation: BNGSim) -> None:
        self._scenario = Scenario("gridmap_v2", name="drag_strip")
        self.vehicle = Vehicle(
            self._car_model, model=self._car_model, licence="MONOLITH"
        )
        self._scenario.add_vehicle(self.vehicle, **self._vehicle_pos)
        self._scenario.make(bng_simulation.bng)
        bng_simulation.start_scenario(self._scenario)

        parts_config_requested = copy.deepcopy(self.params)
        car_config = {"vars": {}, "parts": parts_config_requested}

        self.vehicle.set_part_config(car_config)
        bng_simulation.attach_sensors_to_vehicle(self.vehicle)
        bng_simulation.bng.switch_vehicle(self._car_model)
        bng_simulation.remove_debug_paths()
        bng_simulation.add_debug_path(self._path_nodes)
        self.vehicle.ai.set_script(self._path_nodes)

    def step(
        self, bng_simulation: BNGSim, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        if not self._ready:
            self.reset(bng_simulation)

        if self.done:
            raise ValueError("Finished")

        bng_simulation.bng.step(1)
        sensor_data = bng_simulation.poll_sensors_for_vehicle(self.vehicle)

        self.current_step += 1

        # Check done - finished when x pos is past the node at the end of the drag strip
        self.done = (
            bng_simulation.check_time_limit(self.current_step)
            or sensor_data["state"]["pos"][0] >= self._end_of_ds[0]
        )

        return sensor_data, None, self.done, {}

    def reset(self, bng_simulation: BNGSim):
        self._ready = True
        self.start_scenario(bng_simulation)
        self.done = False
        self.current_step = 0
