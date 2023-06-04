import copy
import glob
from typing import Optional, Any

from gym.spaces import Dict, Text

from beamng_envs.cars.cars_and_configs import CarConfigs

AVAILABLE_PCS = glob.glob("cars_and_configs")


class CrashTestParamSpaceBuilder:
    """
    This param space is dynamic depending on the available car configs.
    """

    _start_position_key = "start_position"
    _speed_key = "speed_kph"
    _car_config_name_key = "car_config_name"
    _g_force_keys = ["gx", "gy", "gz", "gx2", "gy2", "gz2"]

    def __init__(self):
        self._fixed_space = {
            self._speed_key: dict(
                values=(20, 30, 40, 50, 60, 70, 80),
                name=self._speed_key,
                description="Speed, km/h",
                type=float,
                default=30,
            ),
            self._start_position_key: dict(
                values=(
                    "flat_left",
                    "flat_mid",
                    "flat_right",
                    "raised_bar",
                    "bollards_left",
                    "bollards_mid",
                    "bollards_right",
                ),
                name=self._start_position_key,
                description="Start position, name",
                type=str,
                default=30,
            ),
        }

        self._available_car_configs: Optional[Dict[str, Any]] = None
        self.param_space: Optional[Dict[str, Any]] = None
        self.param_space_gym: Optional[Dict[str, Any]] = None

    def _build_basic_space(self):
        if self._available_car_configs is None:
            raise ValueError("Use .build and define the available car configs first.")

        self.param_space = {}
        self.param_space.update(copy.deepcopy(self._fixed_space))
        self.param_space.update(copy.deepcopy(self._available_car_configs))

    def _build_gym_space(self):
        if self.param_space is None:
            self._build_basic_space()

        gym_space = {
            k: Text(
                min_length=1,
                max_length=1,
                charset=[str(val) for val in v["values"]],
            )
            for k, v in self._fixed_space.items()
        }
        gym_space.update(
            {
                self._car_config_name_key: Text(
                    min_length=1,
                    max_length=1,
                    charset=list(self._available_car_configs.keys()),
                )
            }
        )
        self.param_space_gym = Dict(gym_space)

    def build(
        self,
        car_configs: Optional[CarConfigs] = None,
        beamng_path: Optional[str] = None,
    ):
        """
        Create the param space from the available car configs.

        Requires either an existing CarConfigs, or the beamng_path which will be used to find them.
        """
        if car_configs is None:
            if beamng_path is None:
                raise ValueError(
                    "Either existing CarConfigs or beamng_path is required."
                )

            car_configs = CarConfigs.find(beamng_path=beamng_path)

        self._available_car_configs = car_configs.configs

        self._build_basic_space()
        self._build_gym_space()

        return car_configs


if __name__ == "__main__":
    cc = CarConfigs.find(beamng_path="T:/SteamLibrary/steamapps/common/BeamNG.drive/")
    ct_param_space_builder = CrashTestParamSpaceBuilder().build(car_configs=cc)
