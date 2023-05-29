import copy
from typing import Any, Dict, Optional, Tuple

import numpy as np
from beamngpy import Vehicle, Scenario

from beamng_envs.bng_sim.bng_sim import BNGSim
from beamng_envs.interfaces.paradigm import IParadigm


class CrashTestParadigm(IParadigm):
    _car_model = "sunburst"
    _vehicle_pos = dict(pos=(40, 405, 101), rot_quat=(0, 0, -0.707, 0.707))
    _current_step: int

    y_pos = 114
    z_pos = 101
    flat_x = -268
    wedge_x = -224
    bar_x = -246
    bollards_x = -286

    done: bool
    current_step: int
    vehicle: Vehicle

    def __init__(self, params: Dict[str, Any]):
        self.params = params

        self._start_positions = {
            "flat_left": (self.flat_x - 2, self.y_pos, self.z_pos),
            "flat_mid": (self.flat_x, self.y_pos, self.z_pos),
            "flat_right": (self.flat_x + 2, self.y_pos, self.z_pos),
            "raised_bar": (self.bar_x, self.y_pos, self.z_pos),
            "bollards_left": (self.bollards_x + 2, self.y_pos, self.z_pos),
            "bollards_mid": (self.bollards_x, self.y_pos, self.z_pos),
            "bollards_right": (self.bollards_x - 2, self.y_pos, self.z_pos),
            "wedge": (self.wedge_x, self.y_pos, self.z_pos),
        }

        self._rot_quat = (0, 0, -1, 0)
        self.g_force_keys = ["gx", "gy", "gz", "gx2", "gy2", "gz2"]
        self._ready = False

    def _build_path(self, initial_speed_mps: float):
        """
        Build straight part to target, timing according to intended speed.

        Timing assume car is roughly at the intended speed at the start of the path.

        :param initial_speed_mps: Initial speed in ms-1.
        """
        self._n_nodes = 10
        path_target_deltas = np.linspace(0, 120, self._n_nodes)

        times = path_target_deltas / initial_speed_mps

        start_x = self._start_positions[self.params["start_position"]][0]
        start_y = self._start_positions[self.params["start_position"]][1]
        self._path_nodes = [
            {"x": start_x, "y": start_y + y, "z": self.z_pos, "t": t}
            for y, t in zip(path_target_deltas, times)
        ]

    def start_scenario(self, bng_simulation: BNGSim):
        self._scenario = Scenario("gridmap_v2", name="crash_test")
        car_model = self.params["car_config_name"].split("__")[0]
        self.vehicle = Vehicle(car_model, model=car_model, licence="MONOLITH")
        self._scenario.add_vehicle(
            self.vehicle,
            pos=self._start_positions[self.params["start_position"]],
            rot_quat=self._rot_quat,
        )

        self._scenario.make(bng_simulation.bng)
        bng_simulation.start_scenario(self._scenario, load_start_wait=3)

        parts_config = copy.deepcopy(
            bng_simulation.config.car_configs.configs[self.params["car_config_name"]]
        )
        self.vehicle.set_part_config(parts_config)
        bng_simulation.attach_sensors_to_vehicle(self.vehicle)
        bng_simulation.bng.switch_vehicle(self.vehicle)

        speed_mps = float(self.params["speed_kph"]) * 0.27778
        self._build_path(initial_speed_mps=speed_mps)
        self.vehicle.set_velocity(speed_mps)
        self.vehicle.ai.set_script(self._path_nodes)

        bng_simulation.remove_debug_paths()
        bng_simulation.add_debug_path(self._path_nodes)

    def step(
        self, bng_simulation: BNGSim, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        if not self._ready:
            self.reset(bng_simulation)

        if self.done:
            raise ValueError("Finished")

        bng_simulation.bng.step(1, wait=True)
        sensor_data = bng_simulation.poll_sensors_for_vehicle(self.vehicle)
        self.current_step += 1

        # Check done - here always end at max steps
        self.done = bng_simulation.check_time_limit(scenario_step=self.current_step)

        return sensor_data, None, self.done, {}

    def reset(self, bng_simulation: BNGSim):
        self._ready = True
        self.start_scenario(bng_simulation=bng_simulation)
        self.done = False
        self.current_step = 0
