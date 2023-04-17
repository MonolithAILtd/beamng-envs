"""
Runs a single track test, plots results.

For running batches of experiments, see scripts/run_batch_track_tests.py

To run, install requirements and call specifying beamng path options (see readme)

````
pip install -r scripts/requirements.txt
python -m scripts run_single_track_test --beamng_path '' --beamng_user_path ''
````

"""
import argparse
from typing import Optional

import beamngpy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

from beamng_envs import __VERSION__
from beamng_envs.beamng_config import BeamNGConfig
from beamng_envs.envs.track_test.track_test_config import DEFAULT_TRACK_TEST_CONFIG
from beamng_envs.envs.track_test.track_test_disk_results import TrackTestDiskResults
from beamng_envs.envs.track_test.track_test_env import TrackTestEnv
from beamng_envs.envs.track_test.track_test_param_space import (
    TRACK_TEST_PARAM_SPACE_GYM,
)


def plot_track(ts_df: pd.DataFrame, filename: Optional[str] = None):
    """
    Plot track position coloured by speed, and some sample timelines (throttle, brake, gear)

    :param ts_df: The timeseries DataFrame, e.g. from TrackTestDiskResults(path).ts_df.
    :param filename: Optional filename to save plot to, if not set calls plt.show() instead.
    """
    fig, ax = plt.subplots(nrows=3, figsize=(12, 9))
    points = np.array(
        [ts_df["state_pos_0"].values.squeeze(), ts_df["state_pos_1"].values.squeeze()]
    ).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    velocity = (
        np.sqrt(
            ts_df["state_vel_0"] ** 2
            + ts_df["state_vel_1"] ** 2
            + ts_df["state_vel_2"] ** 2
        )
        * 3.6
    ).values[1::]
    norm = plt.Normalize(0, 300)
    lc = LineCollection(segments, cmap="inferno", norm=norm)
    lc.set_array(velocity)
    lc.set_linewidth(20)
    line = ax[0].add_collection(lc)
    ax[0].set_xlim(ts_df["state_pos_0"].min() * 1.2, ts_df["state_pos_0"].max() * 1.2)
    ax[0].set_ylim(ts_df["state_pos_1"].min() * 1.2, ts_df["state_pos_1"].max() * 1.2)
    fig.colorbar(line, ax=ax[0], aspect=8, label="velocity")
    ax[0].set_title("Track position", fontweight="bold")
    ax[0].set_xticklabels([])
    ax[0].set_yticklabels([])

    ax[1].plot(
        ts_df["time_s"], ts_df["electrics_throttle_0"], label="Throttle", linewidth=2
    )
    ax[1].plot(ts_df["time_s"], ts_df["electrics_brake_0"], label="Brake", linewidth=2)
    ax[1].plot(
        ts_df["time_s"], ts_df["electrics_gear_0"] / 6, label="Gear", linewidth=2
    )
    ax[1].set_ylabel("Normalised value", fontweight="bold")
    ax[1].legend(prop={"weight": "bold"})

    ax[2].plot(ts_df["time_s"], ts_df["damage_damage_0"], label="Damage", linewidth=2)
    ax[2].legend(prop={"weight": "bold"})
    ax[2].set_xlabel("Time, s", fontweight="bold")
    ax[2].set_ylabel("Damage sensor value", fontweight="bold")

    fig.tight_layout()
    if filename is not None:
        plt.savefig(filename)
    else:
        plt.show()


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
    opt = parser.parse_args()

    # Setup Python logging to include BeamNG console output
    beamngpy.set_up_simple_logging()

    # Prepare config
    track_test_config = DEFAULT_TRACK_TEST_CONFIG
    track_test_config["output_path"] = opt.output_path
    track_test_config["bng_config"] = BeamNGConfig(
        home=opt.beamng_path, user=opt.beamng_user_path
    )

    # Sample a single set of parameters
    p_set = TRACK_TEST_PARAM_SPACE_GYM.sample()

    # Run the test for each set of parameters
    env = TrackTestEnv(params=p_set, config=track_test_config)

    # Run the env
    results, history = env.run()

    # Previous results can also be reloaded from disk (these are also available in current runs in env.disk_results)
    full_results = TrackTestDiskResults.load(path=env.disk_results.output_path)

    # Get the tabulated results
    timeseries_df = full_results.ts_df

    # Check timing - index for df is timestep, and actual time is also available in a column. This is the Python time;
    # it'll be somewhat variable, but shouldn't be obviously irregular
    time_diff = np.diff(timeseries_df["time_s"])
    mean_time_step = np.round(time_diff.mean() * 1000, 2)
    std_time_step = np.round(time_diff.std() * 1000, 2)
    time_sample = timeseries_df["time_s"].sample(n=50)
    plt.scatter(time_sample.index, time_sample)
    plt.title(f"Time check (mean time step = {mean_time_step} ± {std_time_step} (ms)")
    plt.xlabel("Time, step")
    plt.ylabel("Time, s")
    plt.show()

    plot_track(ts_df=timeseries_df)
