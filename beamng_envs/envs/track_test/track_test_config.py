from beamng_envs.beamng_config import BeamNGConfig

DEFAULT_TRACK_TEST_CONFIG = {
    "max_time": 180,  # Maximum time in seconds
    "error_on_out_of_time": False,  # Whether to raise an error if max_time is reached
    "bng_config": BeamNGConfig(),  # The BeamNG specific config; passed to BeamNGpy
    "output_path": "track_test_results",  # Path to save results to
    "python_hz": 60,  # Frequency of sampling
    "bng_fps": 60,  # Frequency of game physics updates and framerate
    "bng_logging": False,  # Whether to use additional game logging (may cause crashes)
}
