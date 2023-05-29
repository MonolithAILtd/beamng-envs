"""
Define the standard argument parser and defaults used in example scripts.
"""

import argparse

from beamng_envs import __VERSION__

PARSER_BATCH = argparse.ArgumentParser()
PARSER_BATCH.add_argument(
    "--beamng_path",
    type=str,
    default="T:/SteamLibrary/steamapps/common/BeamNG.drive/",
    help="Path to the folder containing Bin64/BeamNG.tech.x64.exe or Bin64/BeamNG.drive.x64.exe.",
)
PARSER_BATCH.add_argument(
    "--beamng_user_path",
    type=str,
    default="C:/beamng_workspace/",
    help="Path to the set-up user workspace.",
)
PARSER_BATCH.add_argument(
    "--output_path",
    type=str,
    default=f"./crash_test_results_v{__VERSION__}",
    help="Output path for results",
)
PARSER_BATCH.add_argument(
    "-N",
    type=int,
    default=200,
    help="The number of tests with randomly selected car setups to run.",
)
PARSER_BATCH.add_argument(
    "--n_jobs",
    type=int,
    default=8,
    help="Number of jobs to use for parallel running.",
)
