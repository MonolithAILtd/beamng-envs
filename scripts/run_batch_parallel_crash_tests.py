"""
Runs a number of crash test experiments in parallel in multiple BeamNG instances.

````
pip install -r scripts/requirements.txt
python -m scripts.run_parallel_crash_tests --beamng_path '' --beamng_user_path '' -N 10 --N_JOBS 3
````

"""

import os
from typing import Any, Dict

import mlflow
import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm

from beamng_envs import __VERSION__
from beamng_envs.bng_sim.beamngpy_config import BeamNGPyConfig
from beamng_envs.bng_sim.bng_sim_worker import BNGSimWorker
from beamng_envs.bng_sim.bng_sim_worker_pool import BNGSimWorkerPool
from beamng_envs.cars.cars_and_configs import CarConfigs
from beamng_envs.envs import TrackTestConfig, CrashTestEnv
from beamng_envs.envs.crash_test.crash_test_config import CrashTestConfig
from beamng_envs.envs.crash_test.crash_test_param_space import (
    CrashTestParamSpaceBuilder,
)
from scripts.args_batch import PARSER_BATCH
from scripts.run_batch_crash_tests import plot_crash


def run_crash_test(worker: BNGSimWorker, conf: TrackTestConfig, p_set: Dict[str, Any]):
    worker.set_busy()
    conf.bng_config = worker.get_config(conf.bng_config)

    env = CrashTestEnv(config=conf, params=p_set)

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
            filename=os.path.join(env.disk_results.output_path, "crash_test_plot.png"),
        )
        mlflow.log_artifacts(env.disk_results.output_path)

    worker.set_free()


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
    mlflow.set_experiment("Crash test example_p")

    # Set up a worker pool to manage separate game instances (including disk workspaces and ports)
    worker_pool = BNGSimWorkerPool(
        user_path="c:\\worker_pool_test\\",
        n_workers=opt.n_jobs,
    )

    # Run in chunks the size of the worker pool. All in batch need to finish before the next batch can start, but it
    # avoids needing to track workers at a higher level - they'll all be free at the end of the batch.
    pool = Parallel(n_jobs=opt.n_jobs)
    for worker_sets in tqdm(
        np.array_split(param_sets, np.ceil(len(param_sets) / opt.n_jobs))
    ):
        jobs = (
            delayed(run_crash_test)(w, crash_test_config, p_set)
            for w, p_set in zip(worker_pool.workers, worker_sets)
        )
        pool(jobs)
