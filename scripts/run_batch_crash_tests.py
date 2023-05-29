import os
import pprint
from typing import Optional

import mlflow
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm

from beamng_envs import __VERSION__
from beamng_envs.bng_sim.beamngpy_config import BeamNGPyConfig
from beamng_envs.cars.cars_and_configs import CarConfigs
from beamng_envs.envs import CrashTestEnv, CrashTestParamSpaceBuilder, CrashTestConfig
from beamng_envs.envs.track_test.track_test_config import TrackTestConfig
from scripts.args_batch import PARSER_BATCH


def plot_crash(sca_ser: pd.Series, ts_df: pd.DataFrame, filename: Optional[str] = None):
    fig, ax = plt.subplots(nrows=2)
    g_force_keys = ["gx", "gy", "gz", "gx2", "gy2", "gz2"]
    ax[0].plot(ts_df["time_s"], ts_df["state_vel_1"], label="velocity")
    for gfk in g_force_keys:
        ax[0].plot(ts_df["time_s"], ts_df[f"g_forces_{gfk}_0"], label=gfk)
    ax[0].legend(loc=6)
    ax[1].plot(ts_df["time_s"], ts_df["damage_damage_0"], label="Total damage")
    ax[1].legend(loc=6)
    ax[1].set_xlabel("Time, s")
    fig.suptitle(
        f"{sca_ser['params_car_config_name']} at {sca_ser['params_speed_kph']} km/h "
        f"into target {sca_ser['params_start_position']} "
    )
    fig.tight_layout()

    if filename is not None:
        plt.savefig(filename)
    else:
        plt.show()


if __name__ == "__main__":
    opt = PARSER_BATCH.parse_args()

    bng_config = BeamNGPyConfig(
        home=opt.beamng_path,
        user=opt.beamng_user_path,
    )

    # Find the available car part configurations
    car_configs = CarConfigs.find(beamng_path=bng_config.home)

    # Use these to build the environment's parameter space
    param_space_space_builder = CrashTestParamSpaceBuilder()
    _ = param_space_space_builder.build(car_configs=car_configs)

    # Sample an example set of parameters for this
    params = param_space_space_builder.param_space_gym.sample()
    # The param space only defines config names, e.g.
    print(params["car_config_name"])
    # The full part config can be looked up in the car_configs used to build the space
    pprint.pprint(car_configs.configs[params["car_config_name"]])

    # The full part configs need to be specified in the environment config so the environment can look them up in a
    # similar manner
    crash_test_config = CrashTestConfig(
        car_configs=car_configs,
        output_path=opt.output_path,
        bng_config=bng_config,
        close_on_done=True,  # This env currently doesn't run reliably when reusing the game instance
    )

    # Sample N sets of parameters
    param_sets = [
        param_space_space_builder.param_space_gym.sample() for _ in range(opt.N)
    ]

    # Set up the mlflow experiment
    mlflow.set_experiment("Crash test example")

    for p_set in tqdm(param_sets):
        env = CrashTestEnv(config=crash_test_config, params=p_set)

        with mlflow.start_run():
            results, history = env.run()

            p_set.update({"version": __VERSION__})
            mlflow.log_params(p_set)
            mlflow.log_metrics(
                {
                    k: v
                    for k, v in results.items()
                    if k not in ["parts_requested", "parts_actual"]
                }
            )

            plot_crash(
                sca_ser=env.disk_results.scalars_series,
                ts_df=env.disk_results.ts_df,
                filename=os.path.join(
                    env.disk_results.output_path, "crash_test_plot.png"
                ),
            )
            mlflow.log_artifacts(env.disk_results.output_path)
