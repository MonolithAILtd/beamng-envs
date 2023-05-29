import os
from typing import Optional

import numpy as np

from beamng_envs.bng_sim.beamngpy_config import BeamNGPyConfig


class BNGSimWorker:
    def __init__(
        self, user_path: str, host: str = "localhost", port: Optional[int] = None
    ):
        self.host = host
        self.port: int = (
            port if port is not None else int(np.random.randint(low=51000, high=65000))
        )
        self.worker_path = os.path.join(user_path, f"port_{self.port}")
        self.busy: bool = False

    def __repr__(self):
        return f"BNGSimWorker referencing a BNGInstance using path {self.worker_path} on {self.host}:{self.port}"

    def get_config(self, bng_config: BeamNGPyConfig):
        bng_config.user = self.worker_path
        bng_config.port = self.port

        return bng_config

    def set_busy(self):
        self.busy = True

    def set_free(self):
        self.busy = False
