from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from beamngpy import Scenario, Vehicle
from beamngpy.types import Float3

from beamng_envs.cars.scintilla_rally import ScintillaRally
from beamng_envs.bng_sim.bng_sim import BNGSim
from beamng_envs.interfaces.paradigm import IParadigm
from beamng_envs.interfaces.types import WAYPOINT_TYPE


class TrackTestParadigm(IParadigm):
    _car_model = "scintilla"
    _car_spawn_pos = dict(pos=(-408.4, 260.23, 25.423), rot_quat=(0, 0, -0.3, 1))
    _car_default_config = ScintillaRally()
    _wp1: WAYPOINT_TYPE = dict(name="quickrace_wp1", pos=[47.0, 256.0, 28.0])
    _wp2: WAYPOINT_TYPE = dict(name="quickrace_wp2", pos=[393.0, -130.0, 34.0])
    _wp3: WAYPOINT_TYPE = dict(name="quickrace_wp3", pos=[-12.0, -65.0, 29.0])
    _wp4: WAYPOINT_TYPE = dict(name="quickrace_wp4", pos=[-220.0, 368.0, 27.0])
    _wp5: WAYPOINT_TYPE = dict(name="quickrace_wp11", pos=[-413.0, 467.0, 34.0])
    _wp6: WAYPOINT_TYPE = dict(name="hr_start", pos=[-402.0, 244.0, 25.0])
    _current_waypoint: Dict[str, Any]
    _current_waypoint_idx: int
    _route_done: List[bool]

    done: bool
    current_step: int
    vehicle: Vehicle

    def __init__(self, params: Dict[str, Any]):
        self.params = params
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
        self._ready = False

    def start_scenario(self, bng_simulation: BNGSim):
        self._scenario = Scenario("hirochi_raceway", "start_line")
        self.vehicle = Vehicle(
            self._car_model, model=self._car_model, licence="MONOLITH"
        )
        self._scenario.add_vehicle(self.vehicle, **self._car_spawn_pos)
        self._scenario.make(bng_simulation.bng)
        bng_simulation.start_scenario(self._scenario)

        pc = self._car_default_config.config.copy()
        pc["vars"].update(
            {k: float(v) for k, v in self.params.items() if k.startswith("$")}
        )

        self.vehicle.set_part_config(pc)
        bng_simulation.attach_sensors_to_vehicle(self.vehicle)
        bng_simulation.bng.switch_vehicle("scintilla")
        self.vehicle.ai_set_mode("manual")
        self.vehicle.ai_set_aggression(float(self.params["driver_aggression"]))
        self.vehicle.ai_set_speed(500, mode="limit")
        self.vehicle.ai_set_waypoint(waypoint=self._current_waypoint["name"])

    def step(
        self, bng_simulation: BNGSim, action: Optional[int] = None, **kwargs
    ) -> Tuple[Optional[Any], Optional[float], bool, Dict[str, Any]]:
        if not self._ready:
            self.reset(bng_simulation)

        if self.done:
            raise ValueError("Finished")

        bng_simulation.bng.step(1)
        sensor_data = bng_simulation.poll_sensors_for_vehicle(self.vehicle)

        # Check if close enough to next waypoint yet
        dist = self._euclidean_distance(
            pos_1=self.vehicle.state["pos"], pos_2=self._current_waypoint["pos"]
        )
        dist_to_finish = self._euclidean_distance(
            pos_1=self.vehicle.state["pos"], pos_2=self._route[-1]["pos"]
        )

        current_time_s = bng_simulation.get_real_time(self.current_step)
        if not (self.current_step % 20):
            print(
                f"{self.current_step} (t={current_time_s}): "
                f"Dist to next waypoint: {dist}"
            )

        if (dist < 150) and (not self._route_done[self._current_waypoint_idx]):
            self._route_done[self._current_waypoint_idx] = True
            self._current_waypoint_idx += 1

            if self._current_waypoint_idx == len(self._route):
                self._current_waypoint = self._final_waypoint
                print(
                    f"{self.current_step} (t={current_time_s}): "
                    f"Setting final waypoint: {self._current_waypoint['name']}"
                )

            else:
                self._current_waypoint = self._route[self._current_waypoint_idx]
                print(
                    f"{self.current_step} (t={current_time_s}): "
                    f"Setting next waypoint: {self._current_waypoint['name']}"
                )

            self.vehicle.ai_set_waypoint(waypoint=self._current_waypoint["name"])

        if np.all(self._route_done) and (dist_to_finish < 3):
            print(
                f"{self.current_step} (t={current_time_s}): "
                f"Within dist thresh of final waypoint, setting done"
            )
            self.done = True

        self.done = self.done or bng_simulation.check_time_limit(self.current_step)
        self.current_step += 1

        sensor_data["dist_to_next_waypoint"] = dist
        sensor_data["current_waypoint"] = self._current_waypoint
        sensor_data["current_waypoint_idx"] = self._current_waypoint_idx

        return sensor_data, None, self.done, {}

    def reset(self, bng_simulation: BNGSim):
        self._current_waypoint_idx = 0
        self._current_waypoint = self._route[self._current_waypoint_idx]
        self._route_done = [False] * len(self._route)
        self._ready = True
        self.start_scenario(bng_simulation)
        self.done = False
        self.current_step = 0

    @staticmethod
    def _euclidean_distance(pos_1: Float3, pos_2: Float3) -> float:
        return np.sqrt(np.sum((np.array(pos_1) - np.array(pos_2)) ** 2))
