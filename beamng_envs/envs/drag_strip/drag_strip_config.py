from dataclasses import dataclass

from beamng_envs.bng_sim.bng_sim_config import BNGSimConfig


@dataclass
class DragStripConfig(BNGSimConfig):
    output_path: str = "drag_strip_results"
    close_on_done: bool = False
    fps: int = 20
