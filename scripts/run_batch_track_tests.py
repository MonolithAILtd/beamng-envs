"""Run a number of samples of car configs in the TrackTestEnv, with logging to MLflow."""
import os

import beamngpy
import mlflow
from beamngpy import BeamNGpy
from tqdm import tqdm

from beamng_envs import __VERSION__
from beamng_envs.beamng_config import BeamNGConfig
from beamng_envs.envs.track_test.track_test_config import TrackTestConfig
from beamng_envs.envs.track_test.track_test_env import TrackTestEnv
from beamng_envs.envs.track_test.track_test_param_space import (
    TRACK_TEST_PARAM_SPACE_GYM,
)
from scripts.args_batch import PARSER_BATCH
from scripts.run_single_track_test import plot_track

if __name__ == "__main__":
    opt = PARSER_BATCH.parse_args()

    # Setup Python logging to include BeamNG console output
    beamngpy.set_up_simple_logging()

    # Prepare config
    track_test_config = TrackTestConfig(
        output_path=opt.output_path,
        bng_close_on_done=False,
        bng_config=BeamNGConfig(
            home=opt.beamng_path,
            user=opt.beamng_user_path
        )
    )

    # Sample N sets of parameters
    param_sets = [TRACK_TEST_PARAM_SPACE_GYM.sample() for _ in range(opt.N)]

    # Set up the mlflow experiment
    mlflow.set_experiment("Track test example")

    # Create a persistent game instance to use to run multiple tests in
    with BeamNGpy(**track_test_config.bng_config.__dict__) as bng:
        # Run the test for each set of parameters
        for p_set in tqdm(param_sets):
            env = TrackTestEnv(
                params=p_set,
                config=track_test_config,
                bng=bng,
            )

            with mlflow.start_run():
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
