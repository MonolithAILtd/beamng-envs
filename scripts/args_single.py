"""
Define the standard argument parser and defaults used in example scripts for single runs.
"""
import argparse

from beamng_envs import __VERSION__

PARSER_SINGLE = argparse.ArgumentParser()
PARSER_SINGLE.add_argument(
    "--beamng_path",
    type=str,
    # default="C:/SteamLibrary/steamapps/common/BeamNG.drive",
    default='C:/Program Files (x86)/Steam/steamapps/common/BeamNG.drive',
    help="Path to the folder containing Bin64/BeamNG.tech.x64.exe or Bin64/BeamNG.drive.x64.exe.",
)
PARSER_SINGLE.add_argument(
    "--beamng_user_path",
    type=str,
    default="C:/beamng_workspace/",
    help="Path to the set-up user workspace.",
)
PARSER_SINGLE.add_argument(
    "--output_path",
    type=str,
    default=f"./track_test_results_v{__VERSION__}",
    help="Output path for results",
)
