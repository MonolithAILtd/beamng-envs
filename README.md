# BeamNG simulation environments

BeamNG.drive/tech based simulation environments.

![Track test](images/readme_example.gif)

# Setup

## Local (Linux or Windows)

1. Obtain and install BeamNG.tech or BeamNG.drive (e.g. from Steam) - https://www.beamng.com/game/
2. Create the intended user path, e.g. ```/beamng_workspace/```
3. Inside that directory create ```ResearchHelper.txt```
4. Create a ```mods``` directory with the version of BeamNG, eg. ```/beamng_workspace/0.25/mods/```
5. Put the ```BeamNGpy.zip``` file included in this repo into the directory created in step 4.
6. Setup a python environment, e.g using Conda:
   ```bash 
   conda create -y --name beamng-envs python=3.8
   conda activate beamng-envs
   ```
7. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

Future details on setting up and using BeamNG via its Python API can be found here https://github.com/BeamNG/BeamNGpy

# Usage

## Running from Python

````python
from beamng_envs.beamng_config import BeamNGConfig
from beamng_envs.envs.track_test.track_test_param_space import TRACK_TEST_PARAM_SPACE_GYM
from beamng_envs.envs.track_test.track_test_config import DEFAULT_TRACK_TEST_CONFIG
from beamng_envs.envs.track_test.track_test_env import TrackTestEnv

track_test_config = DEFAULT_TRACK_TEST_CONFIG
# Set paths are required
track_test_config['bng_config'] = BeamNGConfig(home="/SteamLibrary/steamapps/common/BeamNG.drive",
                                               user="/path/to/beamng/user/workspace/from/setup/above")

param_set = TRACK_TEST_PARAM_SPACE_GYM.sample()
env = TrackTestEnv(params=param_set, config=track_test_config)
results, history = env.run()
````

## Running example script

This script runs a number of tests using random car configurations and logs the results with MLflow.

Update paths as required.

```bash
python -m scripts.run_track_tests -N 5 --beamng_path /SteamLibrary/steamapps/common/BeamNG.drive --beamng_user_path /beamng_workspace/
```

The results and can be viewed using the MLflow UI.

```bash
mlflow ui -h 0.0.0.0 -p 5555
```

http://0.0.0.0:5555

![MLflow UI example](images/mlflow_example.png)

# Compatibility

Each version of the Beamng python api supports specific versions of Beamng -
see https://github.com/BeamNG/BeamNGpy#compatibility

The environments here are compatible with the following versions:

| Beamng version | beamngpy version | beamng-envs version | Supported envs |
|----------------|------------------|---------------------|----------------|
| 0.28           | 1.26             | 0.3.0 - 0.4.0       | Track test     |
| 0.27           | 1.25.1           | 0.3.0               | Track test     |
| 0.26           | 1.24             | 0.2.0               | Track test     |
| 0.24           | 1.22             | 0.1.0               | Track test     |
