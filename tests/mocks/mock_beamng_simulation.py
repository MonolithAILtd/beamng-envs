from unittest.mock import MagicMock

from beamng_envs.bng_sim.bng_sim import BNGSim


class MockBNGSimulation(BNGSim):
    def close(self, *args, **kwargs):
        pass

    def launch(self):
        self.bng = MagicMock()

    def poll_sensors_for_vehicle(self, *args, **kwargs):
        return {
            "state": {
                "rotation": [0, 0, 0],
                "front": [0, 0, 0],
                "vel": [0, 0, 0],
                "up": [0, 0, 0],
                "dir": [0, 0, 0],
                "pos": [0, 0, 0],
            },
            "damage": {"damage": 0},
            "g_forces": {
                "gx": 0,
                "gx2": 0,
                "gy": 0,
                "gy2": 0,
                "gz": 0,
                "gz2": 0,
            },
        }

    def stop_bng_logging_for(self, *args, **kwargs) -> None:
        pass
