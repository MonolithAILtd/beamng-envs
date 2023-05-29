import glob
import json
import os
import pathlib
import shutil
import uuid
import warnings
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from typing import Union, Dict, Any, Optional

import pandas as pd

from beamng_envs import __VERSION__, __BNG_VERSION__
from beamng_envs.data.numpy_json_encoder import NumpyJSONEncoder


class DiskResults:
    """
    Class to handle saving and loading TrackTestEnv results to and from disk

    Automatically assigns each set of results a unique UUID.
    """

    _env_name = "TrackTestEnv"
    _history_fn = "history.json"
    _config_fn = "config.json"
    _bng_config_fn = "bng_config.json"
    _params_fn = "params.json"
    _outcome_fn = "outcome.json"
    _results_fn = "results.json"

    _scalars_series: Optional[pd.Series]
    _ts_df: Optional[pd.DataFrame]
    _bng_ts_df: Optional[pd.DataFrame]

    def __init__(
        self,
        path: str,
        config: Dict[str, Any],
        params: Dict[str, Any],
        results: Dict[str, Any],
        history: Dict[str, Any],
        path_to_bng_logs: Optional[str] = None,
        run_id: Optional[str] = None,
    ):
        self._path = path

        self.config = config
        self.bng_config = config["bng_config"]
        self.results = results
        self.params = params
        self.history = history
        self.path_to_bng_logs = path_to_bng_logs

        self._scalars_series = None
        self._ts_df = None
        self._bng_ts_df = None

        if run_id is None:
            run_id = str(uuid.uuid4())
        self.run_id = run_id

    @property
    def output_path(self) -> str:
        path = os.path.abspath(os.path.join(self.config["output_path"], self.run_id))
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        return path

    def _save_jsons(self):
        # Save parameters, configs, other meta data
        with open(os.path.join(self.output_path, self._bng_config_fn), "w") as f:
            json.dump(self.config["bng_config"].__dict__, f)
        with open(os.path.join(self.output_path, "params.json"), "w") as f:
            json.dump(
                obj={k: v for k, v in self.params.items()}, fp=f, cls=NumpyJSONEncoder
            )
        with open(os.path.join(self.output_path, "config.json"), "w") as f:
            json.dump(
                {k: v for k, v in self.config.items() if k not in ["bng_config"]}, f
            )

        # Save results and history
        with open(os.path.join(self.output_path, self._results_fn), "w") as f:
            json.dump(self.results, f, cls=NumpyJSONEncoder)
        with open(os.path.join(self.output_path, self._history_fn), "w") as f:
            json.dump(self.history, f)

    def _save_bng_logs(self):
        """
        If the bng logs path is specified, and it's different to the main results path, copy the files over and remove
        the original path.
        """
        if (self.path_to_bng_logs is not None) and (
            self.path_to_bng_logs != self._path
        ):
            # Get the beamng vehicle logs
            bng_logs_path = os.path.join(
                self.config["bng_config"].user, __BNG_VERSION__, self.path_to_bng_logs
            )

            try:
                copy_tree(bng_logs_path, self.output_path)
                shutil.rmtree(bng_logs_path)
            except (OSError, DistutilsFileError):
                # Directory may not exist
                pass

    @property
    def outcome(self) -> Dict[str, str]:
        return {"complete": True, "env": self._env_name, "version": __VERSION__}

    def _save_outcome(self):
        # Finally save a small file to flag everything complete runs
        with open(os.path.join(self.output_path, "outcome.json"), "w") as f:
            json.dump(self.outcome, f)

    def save(self):
        self._save_jsons()
        self._save_bng_logs()
        self._save_outcome()

    def _get_scalars_series(self) -> pd.Series:
        scalars_series = []
        for name in ["params", "config", "results", "outcome"]:
            scalars_series.append(
                pd.Series({f"{name}_{k}": v for k, v in getattr(self, name).items()})
            )

        series = pd.concat(scalars_series)
        series["run_id"] = self.run_id

        return series

    @property
    def scalars_series(self) -> pd.Series:
        """
        pd.Series containing scalar values for run.
        """
        if self._scalars_series is None:
            self._scalars_series = self._get_scalars_series()

        return self._scalars_series

    def _get_ts_df(self):
        """
        Currently supports unpacking history with expected keys and either containing singular values or beamng sensor
        data (mostly single-nested dicts).

        TODO: Switch to use History() object to more flexibly handle keys and shapes.
        """

        car_state_key = "car_state"
        time_index_key = "time_s"
        main_sensor_keys = self.history[car_state_key][0].keys()

        dfs = [pd.DataFrame(self.history[time_index_key], columns=[time_index_key])]
        for sensor in main_sensor_keys:
            sensor_data = self.history[car_state_key][0][sensor]
            if isinstance(sensor_data, dict):
                # BeamNG sensor nested dict structure - upack to dict to named columns (some deeper nested dicts may
                # remain)
                for sk in sensor_data.keys():
                    df = pd.DataFrame(
                        data=[t[sensor][sk] for t in self.history[car_state_key]],
                    )
                    df.columns = [f"{sensor}_{sk}_{c}" for c in df]
                    dfs.append(df)
            else:
                # Any singular values saved; column named with original name.
                df = pd.DataFrame(data=[sensor_data], columns=[sensor])
                dfs.append(df)

        return pd.concat(
            (
                *dfs,
                pd.DataFrame(
                    {"run_id": [self.run_id] * len(self.history[time_index_key])}
                ),
            ),
            axis=1,
        )

    @property
    def ts_df(self):
        if self._ts_df is None:
            self._ts_df = self._get_ts_df()

        return self._ts_df

    def _get_bng_ts_df(self) -> Optional[pd.DataFrame]:
        bng_ts_dfs = []
        for fn in glob.glob(os.path.join(self._path, "*.csv")):
            try:
                df = pd.read_csv(fn)
                name = os.path.split(fn)[-1].replace(".csv", "")
                df.columns = [f"{name}_{c}" for c in df]
            except pd.errors.EmptyDataError:
                # Handle the case where this data is invalid
                df = pd.DataFrame()
            bng_ts_dfs.append(df)

        try:
            return pd.concat(bng_ts_dfs, axis=1)
        except ValueError:
            # Nothing to concat
            pass

    @property
    def bng_ts_df(self) -> Optional[pd.DataFrame]:
        """Get the bng logs, if there are any"""
        if (self._bng_ts_df is None) and (self.path_to_bng_logs is not None):
            self._bng_ts_df = self._get_bng_ts_df()

        return self._bng_ts_df

    @classmethod
    def load(cls, path: str) -> [Union[pd.Series, pd.DataFrame]]:
        """
        Load and tabulate previous results saved by a TrackTestEnv.

        :param path: Full path to results, this can be either the raw path, or path to on-disk mlflow logs, e.g.
                       - raw results: '.../track_test_results/{UUID}/'
                       - mmlflow longs: '.../mlruns/{experiment_id}/{run_id}
        :returns: pd.Series containing scalar results/config/params/metrics/etc. and pd.DataFrame containing history
                  timeseries as rows=time step and columns=[sensor]_[sensor_key]_[dimension].
        """
        path = path.replace("\\", "/")

        if "mlruns" in path and "artifacts" not in path:
            path = os.path.join(path, "artifacts")
            run_id = path.split("/")[-2]
        else:
            run_id = os.path.split(path)[-1]

        # Validate results and version
        try:
            with open(os.path.join(path, "outcome.json"), "r") as f:
                outcome = json.load(f)
        except FileNotFoundError:
            raise ValueError(
                f"Unable to load results at {path}: outcome.json not found. Results are either incomplete/invalid, "
                "or path is incorrect"
            )

        results_env = outcome.get("env", "UNKNOWN")
        if results_env != cls._env_name:
            raise ValueError(
                f"Found results for env {results_env}; cannot load these with {str(cls)}"
            )

        results_version = outcome.get("version", "UNKNOWN")
        if results_version != __VERSION__:
            warnings.warn(
                f"Attempting to load results saved from {cls._env_name} version {results_version} using"
                f"{cls._env_name} version {__VERSION__}. This might not work..."
            )

        scalar_json_files = [
            cls._results_fn,
            cls._params_fn,
            cls._config_fn,
            cls._bng_config_fn,
        ]
        scalars = {}
        for fn in scalar_json_files:
            name = os.path.split(fn)[-1].replace(".json", "")
            with open(os.path.join(path, fn), "r") as f:
                scalars[name] = json.load(f)
        bng_config = scalars.pop("bng_config")
        scalars["config"]["bng_config"] = bng_config

        # Load json files containing timeseries
        with open(os.path.join(path, "history.json"), "r") as f:
            history = json.load(f)

        # Check for beamng logs in .csv files, don't load here
        path_to_bng_logs = (
            path if len(glob.glob(os.path.join(path, "*.csv"))) > 0 else None
        )

        results = cls(
            path=path,
            run_id=run_id,
            history=history,
            path_to_bng_logs=path_to_bng_logs,
            **scalars,
        )

        return results
