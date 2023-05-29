import warnings
from dataclasses import dataclass
from typing import Optional

from beamng_envs.bng_sim.beamngpy_config import BeamNGPyConfig
from beamng_envs.cars.cars_and_configs import CarConfigs


@dataclass
class BNGSimConfig:
    # Maximum time in seconds
    max_time: float = 180

    # Whether to raise an error if max_time is reached
    error_on_out_of_time: bool = False

    # The BeamNG specific config; passed to BeamNGpy
    bng_config: BeamNGPyConfig = BeamNGPyConfig()

    # Path to save results to
    output_path: str = "results"

    # Frequency of game physics updates and framerate
    fps: int = 60

    # Whether to use additional game logging (may cause crashes)
    logging: bool = False

    # Whether to close game when finished
    close_on_done: bool = True

    # The car part configs templates available to the beamng simulation; see beamng_envs.cars.CarsAndConfigs.
    # Only required for environments that need to look up available config templates to set from a name, for example,
    # CrashTestEnv.
    car_configs: Optional[CarConfigs] = None

    # Whether to use the advanced BeamNG.tech sensors. False uses just the basic sensors available in BeamNG.drive
    use_tech_sensors: bool = False

    def __post_init__(self):
        if self.fps < 20:
            raise ValueError(f"bng_fps {self.fps} is less than minimum 20 Hz.")

        if self.use_tech_sensors:
            warnings.warn(
                "By default, no .tech sensors are defined, they can be added in "
                "beamng_envs.sensors_set.SensorSet:advanced_sensors"
            )
