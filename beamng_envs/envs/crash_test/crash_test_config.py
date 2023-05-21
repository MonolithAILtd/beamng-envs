from dataclasses import dataclass

from beamng_envs.cars.cars_and_configs import CarConfigs
from beamng_envs.envs.base.default_config import DefaultConfig


@dataclass
class CrashTestConfig(DefaultConfig):
    car_configs: CarConfigs = None
    output_path: str = "crash_test_results"
    bng_close_on_done: bool = False
    max_time: int = 20
    bng_fps: int = 100

    def __post_init__(self):
        if (self.car_configs is None) or (self.car_configs.summary is None):
            raise ValueError("This config requires the car configs; this set should contain the configs expected in the"
                             "parameters space")
