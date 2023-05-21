from dataclasses import dataclass

from beamng_envs.beamng_config import BeamNGConfig


@dataclass
class DefaultConfig:
    max_time: float = 180  # Maximum time in seconds
    error_on_out_of_time: bool = (
        False  # Whether to raise an error if max_time is reached
    )
    bng_config: BeamNGConfig = (
        BeamNGConfig()
    )  # The BeamNG specific config; passed to BeamNGpy
    output_path: str = "results"  # Path to save results to
    bng_fps: int = 60  # Frequency of game physics updates and framerate
    bng_logging: bool = (
        False  # Whether to use additional game logging (may cause crashes)
    )
    bng_close_on_done: bool = True  # Whether to close game when finished

    def __post_init__(self):
        if self.bng_fps < 20:
            raise ValueError(f"bng_fps {self.bng_fps} is less than minimum 20 Hz.")
