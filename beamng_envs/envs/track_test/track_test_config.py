from dataclasses import dataclass

from beamng_envs.bng_sim.bng_sim_config import BNGSimConfig


@dataclass
class TrackTestConfig(BNGSimConfig):
    output_path: str = "track_test_results"
    fps: int = 30
