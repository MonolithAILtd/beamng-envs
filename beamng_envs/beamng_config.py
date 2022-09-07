import os
from dataclasses import dataclass


@dataclass
class BeamNGConfig:
    home: str = os.environ.get('BEAMNG_PATH', '/path/to/beamng')
    user: str = os.environ.get('BEAMNG_USER_PATH', "/beamng_workspace/")
    host: str = os.environ.get('BEAMNG_HOST', 'localhost')
    port: int = int(os.environ.get('BEAMNG_PORT', 64259))
