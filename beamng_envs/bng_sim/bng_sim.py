import time
from typing import Optional, List, Dict, Any

from beamngpy import BeamNGpy, Vehicle, Scenario

from beamng_envs.bng_sim.bng_sim_config import BNGSimConfig
from beamng_envs.envs.errors import OutOfTimeException
from beamng_envs.envs.sensor_set import SensorSet


class BNGSim:
    """
    Manages the BeamNG simulation via the beamnpy.BeamNGpy API.

      - Launching and closing
      - Sensors and sample timing
      - Vehicle logs
      - Debug features such path visualisation
    """

    bng: Optional[BeamNGpy]

    _debug_sphere_ids: Optional[List[int]]
    _debug_line_ids: Optional[List[int]]

    def __init__(self, config: BNGSimConfig, bng: Optional[BeamNGpy] = None):
        """

        :param config:
        :param bng: Optional existing BNG instance to use.
        """
        self.config = config
        self.bng = bng
        self._bng_vehicle_logs = {}
        self._sensor_set = SensorSet(include_tech_sensors=config.use_tech_sensors)

    def launch(self):
        """Launch a BeamNG instance if one doesn't currently exist."""
        if self.bng is None:
            self.bng = BeamNGpy(**self.config.bng_config.__dict__)

        self.bng.open()

    def close(self, force: bool = False):
        """Close the BeamNG instance if it exists and the config allows it to be closed (or force)."""
        if ((self.bng is not None) and self.config.close_on_done) or force:
            self.bng.close()
            self.bng = None
            time.sleep(1)

    def remove_debug_paths(self):
        """Remove debug lines and spheres - these are independent of the scenario state."""
        if getattr(self, "_debug_sphere_ids", None) is not None:
            self.bng.debug.remove_spheres(self._debug_sphere_ids)

        if getattr(self, "_debug_line_ids", None) is not None:
            self.bng.debug.remove_polyline(self._debug_line_ids)

    def add_debug_path(self, path_nodes):
        """Display a path visually with nodes and lines - these are independent of the scenario state."""
        n_nodes = len(path_nodes)
        path_points = [(node["x"], node["y"], node["z"]) for node in path_nodes]

        self._debug_sphere_ids = self.bng.debug.add_spheres(
            coordinates=path_points,
            radii=[0.25 for _ in range(n_nodes)],
            rgba_colors=[(0.5, 0, 0, 0.8) for _ in range(n_nodes)],
            cling=True,
            offset=0.1,
        )
        self._debug_line_ids = self.bng.debug.add_polyline(
            path_points, [0, 0, 0, 0.1], cling=True, offset=0.1
        )

    def check_time_limit(self, scenario_step: int) -> bool:
        """
        Checks the current simulation time limit.

        Optionally raises error on finished simulation

        :params: The current scenario step.
        :return: False for in progress sim, or True for finished simulation (or raise error).
        """
        max_steps = self.config.max_time * self.config.fps
        if scenario_step > max_steps:
            if self.config.error_on_out_of_time:
                raise OutOfTimeException(
                    f"{scenario_step}: Reached max time {self.config.max_time}s "
                    f"({max_steps} steps @ {self.config.fps})."
                )
            else:
                return True

        return False

    def start_bng_logging_for(self, vehicle: Vehicle, scenario_logs_path: str) -> None:
        """Start BNG logging for a vehicle if enabled in config."""

        if self.config.logging:
            vehicle.start_in_game_logging(output_dir=scenario_logs_path)

            self._bng_vehicle_logs[vehicle.name] = scenario_logs_path

    def stop_bng_logging_for(self, vehicle: Vehicle) -> Optional[str]:
        """Stop BNG logging for a vehicle, return the path to these logs."""
        if self.config.logging:
            vehicle.stop_in_game_logging()

            return self._bng_vehicle_logs[vehicle.name]

    def start_scenario(self, scenario: Scenario, load_start_wait: int = 0):
        """
        Load and start a scenario (paused), and ensure graphics/timing settings are applied.

        :param scenario: The beamngpy.Scenario to add to the stimulation.
        :param load_start_wait: Time to wait between loading a loading and starting a scenario. This may help avoid
                                getting stuck on the game loading screen in some cases.
        """
        self.bng.load_scenario(scenario)
        time.sleep(load_start_wait)
        self.bng.start_scenario()
        self.bng.set_steps_per_second(self.config.fps)
        self.bng.apply_graphics_setting()
        self.bng.pause()

    def reset(self):
        self.close()
        self.launch()

    def get_real_time(self, step: int) -> float:
        """Return the real time in seconds for a given step."""
        return step * (1 / self.config.fps)

    def attach_sensors_to_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Attach the managed sensors to a vehicle."""
        return self._sensor_set.attach_to_vehicle(vehicle)

    def poll_sensors_for_vehicle(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Poll the sensors for a vehicle in the simulation."""
        return self._sensor_set.poll_for_vehicle(vehicle)
