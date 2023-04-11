import glob
import json
import os
import pathlib
import shutil
import uuid
import warnings
from distutils.dir_util import copy_tree
from typing import Union, Dict, Any, Optional

import pandas as pd

from beamng_envs import __VERSION__, __BNG_VERSION__


class TrackTestDiskResults:
    """
    Class to handle saving and loading TrackTestEnv results to and from disk

    Automatically assigns each set of results a unique UUID.
    """
    _env_name = "TrackTestEnv"
    _history_fn = 'history.json'
    _config_fn = 'config.json'
    _bng_config_fn = 'bng_config.json'
    _params_fn = 'params.json'
    _outcome_fn = "outcome.json"
    _results_fn = "results.json"

    _scalars_series: Optional[pd.Series]
    _ts_df: Optional[pd.DataFrame]
    _bng_ts_df: Optional[pd.DataFrame]

    def __init__(self,
                 path: str,
                 config: Dict[str, Any],
                 params: Dict[str, Any],
                 results: Dict[str, Any],
                 history: Dict[str, Any],
                 path_to_bng_logs: Optional[str] = None,
                 ):

        self._path = path

        self.config = config
        self.bng_config = config['bng_config']
        self.results = results
        self.params = params
        self.history = history
        self.path_to_bng_logs = path_to_bng_logs

        self._scalars_series = None
        self._ts_df = None
        self._bng_ts_df = None

        self._id = str(uuid.uuid4())

    @property
    def output_path(self) -> str:
        path = os.path.abspath(os.path.join(self.config['output_path'], self._id))
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def _save_jsons(self):
        # Save parameters, configs, other meta data
        json.dump(self.config['bng_config'].__dict__, open(os.path.join(self.output_path, self._bng_config_fn), 'w'))
        json.dump(
            obj={k: float(v) for k, v in self.params.items()},
            fp=open(os.path.join(self.output_path, "params.json"), 'w'),
        )
        json.dump(
            obj={k: v for k, v in self.config.items() if k not in ["bng_config"]},
            fp=open(os.path.join(self.output_path, "config.json"), 'w')
        )

        # Save results and history
        json.dump(self.results, open(os.path.join(self.output_path, self._results_fn), 'w'))
        json.dump(self.history, open(os.path.join(self.output_path, self._history_fn), 'w'))

    def _save_bng_logs(self):
        """
        If the bng logs path is specified, and it's different to the main results path, copy the files over and remove
        the original path.
        """
        if (self.path_to_bng_logs is not None) and (self.path_to_bng_logs != self._path):
            # Get the beamng vehicle logs
            bng_logs_path = os.path.join(self.config["bng_config"].user, __BNG_VERSION__, self.path_to_bng_logs)

            copy_tree(bng_logs_path, self.output_path)
            shutil.rmtree(bng_logs_path)

    def _save_outcome(self):
        # Finally save a small file to flag everything complete runs
        json.dump(
            obj={'complete': True, 'env': self._env_name, 'version': __VERSION__},
            fp=open(os.path.join(self.output_path, "outcome.json"), 'w')
        )

    def save(self):
        self._save_jsons()
        self._save_bng_logs()
        self._save_outcome()

    @property
    def scalars_series(self) -> pd.Series:
        if self._scalars_series is None:

            scalars_series = []
            for name in ["params", "config", "results", "outcome"]:
                scalars_series.append(pd.Series({f"{name}_{k}": v for k, v in getattr(self, name).items()}))

            self._scalars_series = pd.concat(scalars_series)

        return self._scalars_series

    @property
    def ts_df(self):
        if self._ts_df is None:
            car_state_key = 'car_state'
            time_index_key = 'time_s'
            main_sensor_keys = self.history[car_state_key][0].keys()

            dfs = [pd.DataFrame(self.history[time_index_key], columns=[time_index_key])]
            for sensor in main_sensor_keys:
                sensor_keys = self.history[car_state_key][0][sensor].keys()

                for sk in sensor_keys:
                    df = pd.DataFrame(
                        data=[t[sensor][sk] for t in self.history[car_state_key]],
                    )
                    df.columns = [f"{sensor}_{sk}_{c}" for c in df]
                    dfs.append(df)

            self._ts_df = pd.concat(dfs, axis=1)

        return self._ts_df

    @property
    def bng_ts_df(self) -> Optional[pd.DataFrame]:
        """Get the bng logs, if there are any"""
        if (self._bng_ts_df is None) and (self.path_to_bng_logs is not None):
            bng_ts_dfs = []
            for fn in glob.glob(os.path.join(self._path, "*.csv")):
                try:
                    df = pd.read_csv(fn)
                    name = os.path.split(fn)[-1].replace(".csv", '')
                    df.columns = [f"{name}_{c}" for c in df]
                except pd.errors.EmptyDataError:
                    # Handle the case where this data is invalid
                    df = pd.DataFrame()
                bng_ts_dfs.append(df)

            try:
                self._bng_ts_df = pd.concat(bng_ts_dfs, axis=1)
            except ValueError:
                # Nothing to concat
                pass

        return self._bng_ts_df

    @classmethod
    def load(cls, path: str) -> [Union[pd.Series, pd.DataFrame]]:
        """
        Load and tabulate previous results saved by a TrackTestEnv.

        :param path: Full path to results, including UUID, e.g. '.../track_test_results/{UUID}/'
        :returns: pd.Series containing scalar results/config/params/metrics/etc. and pd.DataFrame containing history
                  timeseries as rows=time step and columns=[sensor]_[sensor_key]_[dimension].
        """
        split_path = os.path.split(path)
        path_without_id = os.path.join(*split_path[0:-1])

        # Validate results and version
        try:
            outcome = json.load(open(os.path.join(path, 'outcome.json'), 'r'))
        except FileNotFoundError:
            raise ValueError(
                f"Unable to load results at {path}: outcome.json not found. Results are either incomplete/invalid, "
                "or path is incorrect"
            )

        results_env = outcome.get('env', 'UNKNOWN')
        if results_env != cls._env_name:
            raise ValueError(
                f"Found results for env {results_env}; cannot load these with {str(cls)}"
            )

        results_version = outcome.get('version', 'UNKNOWN')
        if results_version != __VERSION__:
            warnings.warn(
                f"Attempting to load results saved from {cls._env_name} version {results_version} using"
                f"{cls._env_name} version {__VERSION__}. This might not work...")

        scalar_json_files = [cls._results_fn, cls._params_fn, cls._config_fn, cls._bng_config_fn]
        scalars = {}
        for fn in scalar_json_files:
            name = os.path.split(fn)[-1].replace('.json', '')
            scalars[name] = json.load(open(os.path.join(path, fn), 'r'))
        bng_config = scalars.pop("bng_config")
        scalars['config']['bng_config'] = bng_config

        # Load json files containing timeseries
        history = json.load(open(os.path.join(path, "history.json"), 'r'))

        # Check for beamng logs in .csv files, don't load here
        path_to_bng_logs = path_without_id if len(glob.glob(os.path.join(path, "*.csv"))) > 0 else None

        results = cls(
            path=path_without_id,
            history=history,
            path_to_bng_logs=path_to_bng_logs,
            **scalars,
        )
        results._id = split_path[-1]

        return results
