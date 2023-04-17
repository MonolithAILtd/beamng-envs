"""Run a number of samples of car configs in the TrackTestEnv, with logging to MLflow."""
import argparse
import os
import warnings

import beamngpy
import mlflow
from tqdm import tqdm

from beamng_envs import __VERSION__
from beamng_envs.beamng_config import BeamNGConfig
from beamng_envs.envs.track_test.track_test_config import DEFAULT_TRACK_TEST_CONFIG
from beamng_envs.envs.track_test.track_test_env import TrackTestEnv
from beamng_envs.envs.track_test.track_test_param_space import (
    TRACK_TEST_PARAM_SPACE_GYM,
)
from scripts.run_single_track_test import plot_track

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--beamng_path",
        type=str,
        default="T:/SteamLibrary/steamapps/common/BeamNG.drive",
        help="Path to the beamng executable.",
    )
    parser.add_argument(
        "--beamng_user_path",
        type=str,
        default="C:/beamng_workspace/",
        help="Path to the set-up user workspace.",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default=f"./track_test_results_v{__VERSION__}",
        help="Output path for results",
    )
    parser.add_argument(
        "-N",
        type=int,
        default=200,
        help="The number of tests with randomly selected car setups to run.",
    )
    opt = parser.parse_args()

    # Setup Python logging to include BeamNG console output
    beamngpy.set_up_simple_logging()

    # Prepare config
    track_test_config = DEFAULT_TRACK_TEST_CONFIG
    track_test_config["output_path"] = opt.output_path
    track_test_config["bng_config"] = BeamNGConfig(
        home=opt.beamng_path, user=opt.beamng_user_path
    )

    # Sample N sets of parameters
    param_sets = [TRACK_TEST_PARAM_SPACE_GYM.sample() for _ in range(opt.N)]

    # Set up the mlflow experiment
    mlflow.set_experiment("Track test example")

    # Run the test for each set of parameters
    for p_set in tqdm(param_sets):
        env = TrackTestEnv(params=p_set, config=track_test_config)

        with mlflow.start_run():
            try:
                # Run the env
                results, history = env.run()

                # Collect params and metrics, log to MLflow
                params = {k.replace("$", ""): float(v) for k, v in p_set.items()}
                params.update({"version": __VERSION__})
                mlflow.log_params(params)
                mlflow.log_metrics(results)

                # Add a plot of the track
                plot_track(
                    ts_df=env.disk_results.ts_df,
                    filename=os.path.join(
                        env.disk_results.output_path, "track_plot.png"
                    ),
                )
                mlflow.log_artifacts(env.disk_results.output_path)

            except IndexError as e:
                # Depending on the specific setup of the TrackTestEnv, there's a small chance the car will overshoot
                # the start line at the end of the lap without being detected. This will cause an IndexError, usually it
                # can just be ignored
                warnings.warn(f"Caught exception {str(e)}, ignoring.")
