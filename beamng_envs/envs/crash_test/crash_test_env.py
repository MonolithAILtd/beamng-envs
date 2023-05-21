import copy
import time
from typing import Optional, Dict, Iterable, Any, Tuple, List

import numpy as np
from beamngpy import Scenario, Vehicle, BeamNGpy

from beamng_envs.data.disk_results import DiskResults
from beamng_envs.envs.base.env_base import EnvBase
from beamng_envs.envs.crash_test.crash_test_config import CrashTestConfig

Y_POS = 114
Z_POS = 101
FLAT_X = -268
WEDGE_X = -224
BAR_X = -246
BOLLARDS_X = -286
FLAT_X = -268


class CrashTestEnv(EnvBase):
    _current_step: int
    _start_positions = {
        'flat_left': (FLAT_X - 2, Y_POS, Z_POS),
        'flat_mid': (FLAT_X, Y_POS, Z_POS),
        'flat_right': (FLAT_X + 2, Y_POS, Z_POS),
        'raised_bar': (BAR_X, Y_POS, Z_POS),
        'bollards_left': (BOLLARDS_X + 2, Y_POS, Z_POS),
        'bollards_mid': (BOLLARDS_X, Y_POS, Z_POS),
        'bollards_right': (BOLLARDS_X - 2, Y_POS, Z_POS),
        'wedge': (WEDGE_X, Y_POS, Z_POS)
    }
    _rot_quat = (0, 0, -1, 0)
    _g_force_keys = ['gx', 'gy', 'gz', 'gx2', 'gy2', 'gz2']

    config: CrashTestConfig

    def __init__(
            self,
            params: Dict[str, Any],
            config: CrashTestConfig,
            bng: Optional[BeamNGpy] = None,
    ):
        super().__init__(params=params, config=config, bng=bng)
        self._soft_reset()

    def _make_scenario(self):
        self._scenario = Scenario("gridmap_v2", name="crash_test")
        car_model = self.params['car_config_name'].split('__')[0]
        self._vehicle = Vehicle(
            car_model, model=car_model, licence="MONOLITH"
        )
        self._scenario.add_vehicle(
            self._vehicle,
            pos=self._start_positions[self.params['start_position']],
            rot_quat=self._rot_quat,
        )
        self._scenario.make(self._bng)

    def _build_path(self, initial_speed_mps: float):
        """
        Build straight part to target, timing according to intended speed.

        Timing assume car is roughly at the intended speed at the start of the path.

        :param initial_speed_mps: Initial speed in ms-1.
        """
        self._n_nodes = 10
        path_target_deltas = np.linspace(0, 120, self._n_nodes)

        times = path_target_deltas / initial_speed_mps

        start_x = self._start_positions[self.params['start_position']][0]
        start_y = self._start_positions[self.params['start_position']][1]
        self._path_nodes = [
            {"x": start_x, "y": start_y + y, "z": Z_POS, "t": t}
            for y, t in zip(path_target_deltas, times)
        ]

    def _set_vehicle_config(self):
        parts_config = copy.deepcopy(self.config.car_configs.configs[self.params['car_config_name']])
        self._vehicle.set_part_config(parts_config)
        self._parts_actual = self._vehicle.get_part_config()
        self._attach_sensors()
        speed_mps = float(self.params['speed_kph']) * 0.27778
        self._build_path(initial_speed_mps=speed_mps)
        self._remove_debug_paths()
        self._add_debug_path(self._path_nodes)
        self._vehicle.set_velocity(speed_mps)
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

        # Check done - here always end at max steps
        self.done = self._current_step >= (self.config.max_time * self.config.bng_fps)

        return sensor_data, None, self.done, {}

    def run(
            self, modifiers: Optional[Dict[str, Iterable[Any]]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, List[Any]]]:
        self._run_to_done()

        self.results["parts_requested"] = self.params
        self.results["parts_actual"] = self._parts_actual
        self.results["max_damage"] = np.max([v['damage']['damage'] for v in self.history[self._car_state_key]])
        g_force_maxs = {}
        for k in self._g_force_keys:
            g_force_maxs[f"max_abs_{k}"] = np.max(np.abs([t['g_forces'][k] for t in self.history[self._car_state_key]]))
        self.results.update(g_force_maxs)

        config_dict = copy.deepcopy(self.config.__dict__)
        _ = config_dict.pop('car_configs')

        self.disk_results = DiskResults(
            path=self.config.output_path,
            params=self.params,
            config=config_dict,
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
        # There's an issue in this env with reusing BeamNG game - it gets stuck when loading a new scenario after the
        # first, sleeping here appears to reduce the chance of this happening.
        time.sleep(1)
        self._start_scenario()
        self._set_vehicle_config()
        self._soft_reset()
