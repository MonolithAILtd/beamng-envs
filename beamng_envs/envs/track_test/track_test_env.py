import time
import warnings
from typing import Optional, Dict, Iterable, Any, Tuple, List, Sequence

import numpy as np
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import State
from beamngpy.types import Float3
from gym import Space

from beamng_envs.beamng_config import BeamNGConfig
from beamng_envs.cars.scintilla_rally import ScintillaRally
from beamng_envs.envs.track_test.track_test_config import DEFAULT_TRACK_TEST_CONFIG
from beamng_envs.envs.track_test.track_test_param_space import TRACK_TEST_PARAM_SPACE_GYM
from beamng_envs.interfaces.env import IEnv
from beamng_envs.interfaces.types import WAYPOINT_TYPE


class OutOfTimeException(Exception):
    pass


class TrackTestEnv(IEnv):
    """
    Prototype track test environment.

    Loads the Scintilla rally car, exposes some of the part variables in the parameter space. The same parts are always
    used, but their settings can be changed.

    Runs a lap of part of the Hirochi Raceway circuit by setting checkpoints as the car nears them. It uses the inbuilt
    AI with customisable aggressiveness - it's worth setting a max time as the AI can crash if it's too aggressive with
    a bad car setup.

    Good laps are around ~85s.

    See scripts/ for some usage examples.

    TODO:
        - Switch time from Python -> BNG control
        - Switch to using a lap config rather than manual checkpoint based route definition - it'll likely be simpler
          and cause fewer odd behaviours in the AI.
    """
    param_space: Space = TRACK_TEST_PARAM_SPACE_GYM
    _car_model = 'scintilla'
    _car_spawn_pos = dict(pos=(-408.4, 260.23, 25.423), rot_quat=(0, 0, -0.3, 1))
    _car_default_config = ScintillaRally()
    _wp1: WAYPOINT_TYPE = dict(name='quickrace_wp1', pos=[47., 256., 28.])
    _wp2: WAYPOINT_TYPE = dict(name='quickrace_wp2', pos=[393., -130., 34.])
    _wp3: WAYPOINT_TYPE = dict(name='quickrace_wp3', pos=[-12., -65., 29.])
    _wp4: WAYPOINT_TYPE = dict(name='quickrace_wp4', pos=[-220., 368., 27.])
    _wp5: WAYPOINT_TYPE = dict(name='quickrace_wp11', pos=[-413., 467., 34.])
    _wp6: WAYPOINT_TYPE = dict(name='hr_start', pos=[-402., 244., 25.])

    _bng: Optional[BeamNGpy] = None
    _scenario: Scenario
    _vehicle: Vehicle
    _current_waypoint: Dict[str, Any]
    _current_waypoint_idx: int
    _current_time: float
    _start_time: float
    _current_step: int
    done: bool
    results: Dict[str, Any]
    history: Dict[str, List[Any]]

    def __init__(self, params: Dict[str, Any], config: Dict[str, Any] = DEFAULT_TRACK_TEST_CONFIG):

        self.params: Dict[str, Any] = params
        self.config: Dict[str, Any] = config
        self._bng = None
        # Route over short tack - start line (spawn point) to start line
        self._route: List[WAYPOINT_TYPE] = [self._wp1, self._wp2, self._wp3, self._wp4, self._wp5, self._wp6]
        # Used to keep the car racing over the finish line, rather than try to stop on it.
        self._final_waypoint = self._wp1

        self._soft_reset()

    def launch(self):
        if self._bng is None:
            self._bng = BeamNGpy(**self.config.get('bng_config', BeamNGConfig()).__dict__)
            self._bng.open()

    def close(self):
        if self._bng is not None:
            self._bng.close()
            self._bng = None
            time.sleep(1)

    def _start_scenario(self):
        self._scenario = Scenario('hirochi_raceway', "start_line")
        self._vehicle = Vehicle(self._car_model, model=self._car_model, licence='MONOLITH')
        self._scenario.add_vehicle(self._vehicle, **self._car_spawn_pos)
        self._scenario.make(self._bng)
        self._bng.load_scenario(self._scenario)
        self._bng.start_scenario()

    def _set_vehicle_config(self):
        pc = self._car_default_config.config.copy()
        pc['vars'].update({k: float(v) for k, v in self.params.items() if k.startswith('$')})

        self._vehicle.set_part_config(pc)
        self._vehicle.sensors.attach("state", State())
        self._bng.switch_vehicle('scintilla')

    def _set_driver_config(self):
        self._vehicle.ai_set_mode('manual')
        self._vehicle.ai_set_aggression(float(self.params['driver_aggression']))
        self._vehicle.ai_set_speed(500, mode='limit')

    @staticmethod
    def _euclidian_distance(pos_1: Float3, pos_2: Float3) -> float:
        return np.sqrt(np.sum((np.array(pos_1) - np.array(pos_2)) ** 2))

    def step(self, action: Optional[int] = None, **kwargs) -> Tuple[Optional[Any], Optional[float],
                                                                    bool, Dict[str, Any]]:
        """

        :param action:
        :param kwargs:
        :return: Tuple containing (observation, reward, done, info) (to match OpenAI Gym interface).
        """

        if self.done:
            raise ValueError('Already finished')

        if self._current_step == 0:
            self.reset()
            self._vehicle.ai_set_waypoint(waypoint=self._current_waypoint['name'])

        # Check if close enough to next waypoint yet
        self._vehicle.sensors.poll()
        dist = self._euclidian_distance(pos_1=self._vehicle.state['pos'],
                                        pos_2=self._current_waypoint['pos'])
        dist_to_finish = self._euclidian_distance(pos_1=self._vehicle.state['pos'],
                                                  pos_2=self._route[-1]['pos'])

        if not (self._current_step % 20):
            print(f"{self._current_step} (t={self._current_time}): Dist to next way point: {dist}")

        if (dist < 150) and (not self._route_done[self._current_waypoint_idx]):
            self._route_done[self._current_waypoint_idx] = True
            self._current_waypoint_idx += 1

            if self._current_waypoint_idx == len(self._route):
                self._current_waypoint = self._final_waypoint
                print(f"{self._current_step} (t={self._current_time}): "
                      f"Setting final waypoint: {self._current_waypoint['name']}")

            else:
                self._current_waypoint = self._route[self._current_waypoint_idx]
                print(f"{self._current_step} (t={self._current_time}): "
                      f"Setting next waypoint: {self._current_waypoint['name']}")

            self._vehicle.ai_set_waypoint(waypoint=self._current_waypoint['name'])

        if np.all(self._route_done) and (dist_to_finish < 3):
            print(f"{self._current_step} (t={self._current_time}): "
                  f"Within dist thresh of final waypoint, setting done")
            self.done = True

        self._current_time = time.time() - self._start_time
        self._current_step += 1

        if self._current_time > self.config['max_time']:
            self.done = True
            raise OutOfTimeException(f"{self._current_step}: Reached max time {self.config['max_time']}")

        return self._vehicle.sensors['state'].data, None, self.done, {}

    def run(self, modifiers: Optional[Dict[str, Iterable[Any]]] = None) -> Tuple[Dict[str, Any],
                                                                                 Dict[str, Sequence[Any]]]:
        try:
            while not self.done:
                obs, _, done, _ = self.step()
                self.history["car_state"].append(obs)
                time.sleep(0.01)
        except OutOfTimeException as te:
            if self.config.get('error_on_out_of_time', False):
                raise te
            else:
                warnings.warn(str(te))
                finished = 0
        else:
            finished = 1
        finally:
            self.close()

        self.results = {'lap_time': self._current_time, 'finished': finished}
        print(f'Lap time: {np.round(self.results["lap_time"], 3)} s')
        return self.results, self.history

    def reset(self):
        self.close()
        self.launch()
        self._start_scenario()
        self._set_vehicle_config()
        self._set_driver_config()
        self._soft_reset()

    def _soft_reset(self):
        self.done = False
        self._current_step = 0
        self._current_waypoint_idx = 0
        self._current_waypoint = self._route[self._current_waypoint_idx]
        self._current_time = 0.0
        self._route_done = [False] * len(self._route)
        self.history = {'car_state': []}
        self.results = {}
        self._start_time = time.time()
