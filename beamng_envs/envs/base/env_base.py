import abc
import copy
import os
import time
import uuid
import warnings
from typing import Optional, Dict, Any, List

import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Sensor, State, Electrics, GForces, Damage
from beamngpy.types import Float3

from beamng_envs.data.disk_results import DiskResults
from beamng_envs.envs.base.default_config import DefaultConfig
from beamng_envs.envs.errors import OutOfTimeException
from beamng_envs.interfaces.env import IEnv


class EnvBase(IEnv, abc.ABC):
    done: bool
    results: Dict[str, Any]
    disk_results: Optional[DiskResults]
    history: Dict[str, List[Any]]
    _car_model: str
    _scenario: Scenario
    _vehicle: Vehicle
    _sensors = Dict[str, Sensor]
    _start_time: float
    _current_time: float
    _current_step: int
    _debug_sphere_ids: Optional[Any]
    _debug_line_ids: Optional[Any]

    def __init__(
            self,
            params: Dict[str, Any],
            config: DefaultConfig = DefaultConfig,
            bng: Optional[BeamNGpy] = None,
    ):
        self.params = params
        self.config = config
        self._bng = bng
        self._bng_logs_path = os.path.join(self.__class__.__name__, str(uuid.uuid4()))
        self._time_key = "time_s"
        self._time_taken_key = "time"
        self._car_state_key = "car_state"
        self._step_key = "time_pts"

    @property
    def _current_time(self) -> float:
        """Return current time in seconds"""
        return self._current_step / self.config.bng_fps

    def launch(self):
        if self._bng is None:
            self._bng = BeamNGpy(**self.config.bng_config.__dict__)

        self._bng.open()

    def close(self):
        if (self._bng is not None) and self.config.bng_close_on_done:
            self._bng.close()
            self._bng = None
            time.sleep(1)

    @abc.abstractmethod
    def _make_scenario(self):
        pass

    def _start_scenario(self):
        self._bng.load_scenario(self._scenario)
        self._bng.start_scenario()
        self._bng.set_steps_per_second(self.config.bng_fps)
        self._bng.apply_graphics_setting()
        self._bng.pause()

    @staticmethod
    def _euclidean_distance(pos_1: Float3, pos_2: Float3) -> float:
        return np.sqrt(np.sum((np.array(pos_1) - np.array(pos_2)) ** 2))

    def _set_sensors(self):
        self._sensors = dict(
            state=State(),
            electrics=Electrics(),
            g_forces=GForces(),
            damage=Damage(),
            # imu=IMU(pos=(0, 0, 0), name='imu'),  # Causing LUA error on attach
        )

    def _attach_sensors(self):
        for sensor_name, sensor in self._sensors.items():
            self._vehicle.sensors.attach(sensor_name, sensor)

    def _poll_vehicle_sensors(self):
        self._vehicle.sensors.poll()
        sensor_data = copy.deepcopy(
            {k: self._vehicle.sensors[k].data for k in self._sensors.keys()}
        )

        return sensor_data

    def _check_done(self):
        if self.done:
            raise ValueError("Already finished")

    def _step_zero(self):
        self.reset()

        if self.config.bng_logging:
            self._vehicle.start_in_game_logging(output_dir=self._bng_logs_path)

    def _check_time_limit(self):
        max_steps = self.config.max_time * self.config.bng_fps
        if self._current_step > max_steps:
            self.done = True
            raise OutOfTimeException(
                f"{self._current_step}: Reached max time {self.config.max_time}s "
                f"({max_steps} steps @ {self.config.bng_fps})."
            )

    def _remove_debug_paths(self):
        """
        Remove debug lines and spheres - these persist across scenarios.
        """
        if getattr(self, '_debug_sphere_ids', None) is not None:
            self._bng.debug.remove_spheres(self._debug_sphere_ids)

        if getattr(self, '_debug_line_ids', None) is not None:
            self._bng.debug.remove_polyline(self._debug_line_ids)

    def _add_debug_path(self, path_nodes):
        """
        Display a path visually with nodes and lines.
        """
        n_nodes = len(path_nodes)
        path_points = [
            (node["x"], node["y"], node["z"]) for node in path_nodes
        ]

        self._debug_sphere_ids = self._bng.debug.add_spheres(
            coordinates=path_points,
            radii=[0.25 for _ in range(n_nodes)],
            rgba_colors=[(0.5, 0, 0, 0.8) for _ in range(n_nodes)],
            cling=True,
            offset=0.1,
        )
        self._debug_line_ids = self._bng.debug.add_polyline(
            path_points, [0, 0, 0, 0.1], cling=True, offset=0.1
        )

    def _run_to_done(self):
        try:
            while not self.done:
                self._check_time_limit()

                obs, _, done, _ = self.step()
                self.history[self._car_state_key].append(obs)
                self.history[self._time_key].append(self._current_time)
                self.history[self._step_key].append(self._current_step)
        except OutOfTimeException as te:
            if self.config.error_on_out_of_time:
                raise te
            else:
                warnings.warn(str(te))
                finished = 0
        else:
            finished = 1
        finally:
            if self.config.bng_logging:
                self._vehicle.stop_in_game_logging()
            self.close()

        self.results = {self._time_taken_key: self._current_time, "finished": finished}
        print(f'Time taken: {np.round(self.results[self._time_taken_key], 3)} s')

    def _clear_history(self):
        self.history = {
            self._car_state_key: [],
            self._time_key: [],
            self._step_key: [],
        }
        self._current_step = 0
        self.results = {}

    def _soft_reset(self):
        self._set_sensors()
        self._clear_history()
        self.done = False
        self._start_time = time.time()
