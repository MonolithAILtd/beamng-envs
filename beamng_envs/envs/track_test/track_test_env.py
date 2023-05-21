from typing import Optional, Dict, Iterable, Any, Tuple, List, Sequence

import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle
from gym import Space

from beamng_envs.cars.scintilla_rally import ScintillaRally
from beamng_envs.data.disk_results import DiskResults
from beamng_envs.envs.base.env_base import EnvBase
from beamng_envs.envs.track_test.track_test_config import TrackTestConfig
from beamng_envs.envs.track_test.track_test_param_space import (
    TRACK_TEST_PARAM_SPACE_GYM,
)
from beamng_envs.interfaces.types import WAYPOINT_TYPE


class TrackTestEnv(EnvBase):
    """
    Prototype track test environment.

    Loads the Scintilla rally car, exposes some part variables in the parameter space. The same parts are always
    used, but their settings can be changed.

    Runs a lap of part of the Hirochi Raceway circuit by setting checkpoints as the car nears them. It uses the inbuilt
    AI with customisable aggressiveness - it's worth setting a max time as the AI can crash if it's too aggressive with
    a bad car setup.

    Good laps are around ~85s.

    See scripts/ for some usage examples.

    TODO:
        - Switch to using a lap config rather than manual checkpoint based route definition - it'll likely be simpler
          and cause fewer odd behaviours in the AI.
    """

    param_space: Space = TRACK_TEST_PARAM_SPACE_GYM
    _car_model = "scintilla"
    _car_spawn_pos = dict(pos=(-408.4, 260.23, 25.423), rot_quat=(0, 0, -0.3, 1))
    _car_default_config = ScintillaRally()
    _wp1: WAYPOINT_TYPE = dict(name="quickrace_wp1", pos=[47.0, 256.0, 28.0])
    _wp2: WAYPOINT_TYPE = dict(name="quickrace_wp2", pos=[393.0, -130.0, 34.0])
    _wp3: WAYPOINT_TYPE = dict(name="quickrace_wp3", pos=[-12.0, -65.0, 29.0])
    _wp4: WAYPOINT_TYPE = dict(name="quickrace_wp4", pos=[-220.0, 368.0, 27.0])
    _wp5: WAYPOINT_TYPE = dict(name="quickrace_wp11", pos=[-413.0, 467.0, 34.0])
    _wp6: WAYPOINT_TYPE = dict(name="hr_start", pos=[-402.0, 244.0, 25.0])

    _bng: Optional[BeamNGpy] = None
    _current_waypoint: Dict[str, Any]
    _current_waypoint_idx: int
    disk_results: Optional[DiskResults]

    def __init__(
            self,
            params: Dict[str, Any],
            config: TrackTestConfig = TrackTestConfig(),
            bng: Optional[BeamNGpy] = None,
    ):
        super().__init__(params=params, config=config, bng=bng)
        # Route over short tack - start line (spawn point) to start line
        self._route: List[WAYPOINT_TYPE] = [
            self._wp1,
            self._wp2,
            self._wp3,
            self._wp4,
            self._wp5,
            self._wp6,
        ]
        # Used to keep the car racing over the finish line, rather than try to stop on it.
        self._final_waypoint = self._wp1

        self.disk_results = None

        self._soft_reset()

    def _make_scenario(self):
        self._scenario = Scenario("hirochi_raceway", "start_line")
        self._vehicle = Vehicle(
            self._car_model, model=self._car_model, licence="MONOLITH"
        )
        self._scenario.add_vehicle(self._vehicle, **self._car_spawn_pos)
        self._scenario.make(self._bng)

    def _set_vehicle_config(self):
        pc = self._car_default_config.config.copy()
        pc["vars"].update(
            {k: float(v) for k, v in self.params.items() if k.startswith("$")}
        )

        self._vehicle.set_part_config(pc)
        self._attach_sensors()
        self._bng.switch_vehicle("scintilla")

    def _set_driver_config(self):
        self._vehicle.ai_set_mode("manual")
        self._vehicle.ai_set_aggression(float(self.params["driver_aggression"]))
        self._vehicle.ai_set_speed(500, mode="limit")

    def step(
            self, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        """

        :param action:
        :param kwargs:
        :return: Tuple containing (observation, reward, done, info) (to match OpenAI Gym interface).
        """

        self._check_done()
        if self._current_step == 0:
            self._step_zero()
            self._vehicle.ai_set_waypoint(waypoint=self._current_waypoint["name"])

        self._bng.step(1, wait=True)
        sensor_data = self._poll_vehicle_sensors()

        # Check if close enough to next waypoint yet
        dist = self._euclidean_distance(
            pos_1=self._vehicle.state["pos"], pos_2=self._current_waypoint["pos"]
        )
        dist_to_finish = self._euclidean_distance(
            pos_1=self._vehicle.state["pos"], pos_2=self._route[-1]["pos"]
        )

        if not (self._current_step % 20):
            print(
                f"{self._current_step} (t={self._current_time}): Dist to next waypoint: {dist}"
            )

        if (dist < 150) and (not self._route_done[self._current_waypoint_idx]):
            self._route_done[self._current_waypoint_idx] = True
            self._current_waypoint_idx += 1

            if self._current_waypoint_idx == len(self._route):
                self._current_waypoint = self._final_waypoint
                print(
                    f"{self._current_step} (t={self._current_time}): "
                    f"Setting final waypoint: {self._current_waypoint['name']}"
                )

            else:
                self._current_waypoint = self._route[self._current_waypoint_idx]
                print(
                    f"{self._current_step} (t={self._current_time}): "
                    f"Setting next waypoint: {self._current_waypoint['name']}"
                )

            self._vehicle.ai_set_waypoint(waypoint=self._current_waypoint["name"])

        if np.all(self._route_done) and (dist_to_finish < 3):
            print(
                f"{self._current_step} (t={self._current_time}): "
                f"Within dist thresh of final waypoint, setting done"
            )
            self.done = True

        self._current_step += 1

        sensor_data['dist_to_next_waypoint'] = dist
        sensor_data['current_waypoint'] = self._current_waypoint
        sensor_data['current_waypoint_idx'] = self._current_waypoint_idx

        return sensor_data, None, self.done, {}

    def run(
            self, modifiers: Optional[Dict[str, Iterable[Any]]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Sequence[Any]]]:
        self._run_to_done()

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

    def reset(self):
        self.close()
        self.launch()
        self._make_scenario()
        self._start_scenario()
        self._set_vehicle_config()
        self._set_driver_config()
        self._soft_reset()

    def _soft_reset(self):
        self._set_sensors()
        self._clear_history()
        self.done = False
        self._current_waypoint_idx = 0
        self._current_waypoint = self._route[self._current_waypoint_idx]
        self._route_done = [False] * len(self._route)
