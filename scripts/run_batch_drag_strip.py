"""
Run the DragStrip environment a number of times, load and compare results.
"""
import os

import mlflow
from beamngpy import BeamNGpy
from matplotlib import pyplot as plt

from beamng_envs import __VERSION__
from beamng_envs.bng_sim.beamngpy_config import BeamNGPyConfig

from beamng_envs.envs.drag_strip.drag_strip_config import DragStripConfig
from beamng_envs.envs.drag_strip.drag_strip_env import DragStripEnv
from scripts.args_batch import PARSER_BATCH


if __name__ == "__main__":
    opt = PARSER_BATCH.parse_args()

    config = DragStripConfig(
        bng_config=BeamNGPyConfig(
            home=opt.beamng_path,
            user=opt.beamng_user_path,
        ),
        fps=30,
        max_time=30,
        bng_close_on_done=False,
        error_on_out_of_time=False,
    )
    bng = BeamNGpy(**config.bng_config.__dict__)

    for run in range(opt.N):
        params = DragStripEnv.param_space.sample()

        with mlflow.start_run():
            env = DragStripEnv(params=params, config=config, bng=bng)
            results, _ = env.run()

            fig, ax = plt.subplots()
            ax.plot(
                env.history["time_s"],
                [t["state"]["pos"][0] for t in env.history["car_state"]],
                label=f"run {run}",
            )
            ax.set_xlabel("Time")
            ax.set_ylabel("Distance travelled")
            ax.legend()
            filename = os.path.join(env.disk_results.output_path, "drag_strip_plot.png")
            plt.savefig(filename)
            plt.close(fig)

            # Log to MLflow
            mlflow.log_params({"version": __VERSION__})
            mlflow.log_metrics(results)
            mlflow.log_artifacts(env.disk_results.output_path)
