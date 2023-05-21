from dataclasses import dataclass

from beamng_envs.envs.base.default_config import DefaultConfig


@dataclass
class DragStripConfig(DefaultConfig):
    output_path: str = "drag_strip_results"
    bng_close_on_done: bool = False
