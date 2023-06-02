import ast
import glob
import json
import os
import pathlib
import tempfile
import warnings
import zipfile
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError
from tqdm import tqdm
from typing_extensions import Literal

PART_CONFIG_TYPE = Dict[Literal["format", "model", "parts"], Dict[str, str]]

CARS = [
    "atv",
    "autobello",
    "barstow",
    "bastion",
    "bluebuck",
    "bolide",
    "burnside",
    "citybus",
    "coupe",
    "covet",
    "etk800",
    "etkc",
    "etki",
    "fullsize",
    "hopper",
    "legran",
    "midsize",
    "midtruck",
    "miramar",
    "moonhawk",
    "pessima",
    "pickup",
    "pigeon",
    "racetruck",
    "roamer",
    "rockbouncer",
    "sbr",
    "scintilla",
    "semi",
    "sunburst",
    "van",
    "vivace",
    "wendover",
    "wigeon",
]


@dataclass
class CarConfigs:
    path: str = "cars_and_configs"
    include_cars: Optional[List[str]] = None

    summary: Dict[str, Dict[str, str]] = field(init=False, repr=False, default=None)
    configs: Dict[str, PART_CONFIG_TYPE] = field(
        init=False, default_factory=lambda: {}, repr=False
    )

    def __post_init__(self):
        self._load_part_configs()

    def _load_part_configs(
        self,
        summary_file: str = "cars_and_configs/cars_and_configs.json",
    ) -> None:
        with open(summary_file, "r") as f:
            self.summary = json.load(f)

        for car, configs_dict in self.summary.items():
            for config_name, config_path in configs_dict.items():
                with open(config_path, "r") as f:
                    self.configs[f"{car}__{config_name}"] = json.load(f)

    @classmethod
    def find(
        cls,
        beamng_path: str = "T:/SteamLibrary/steamapps/common/BeamNG.drive/",
        output_path: str = "cars_and_configs",
    ):
        """Find valid part configs."""

        if os.path.exists(os.path.join(output_path, "cars_and_configs.json")):
            return cls(path=output_path)

        cls._find_part_configs(beamng_path=beamng_path)

        return cls(
            path=output_path,
            include_cars=None,
        )

    @staticmethod
    def _try_parse_file(
        path: str, extracted_path: str, out_path: str, verbose: bool
    ) -> Tuple[Dict[str, str], bool]:
        try:
            with open(path, "r") as f:
                try:
                    loader = YAML()
                    loader.allow_duplicate_keys = True
                    parsed_json = loader.load(f)
                except (ParserError, ScannerError) as e1:
                    parsed_json = ast.literal_eval(f.read().replace("\n", ""))
            # And re-save into output dir in valid json
            dst_path = path.replace(extracted_path, str(out_path)).replace(
                ".pc", ".json"
            )
            with open(dst_path, "w") as f:
                json.dump(parsed_json, f)

            return {os.path.split(path)[1].replace(".pc", ""): dst_path}, True

        except SyntaxError as e2:
            if verbose:
                warnings.warn(f"Failed to parse {path} due to {e2}.")

            return {}, False

    @staticmethod
    def _find_part_configs(
        beamng_path: str,
        output_path: str = "cars_and_configs",
        verbose: bool = False,
    ) -> None:
        veh_zips = glob.glob(os.path.join(beamng_path, "content", "vehicles", "*.zip"))
        car_zips = [
            v for v in veh_zips if os.path.split(v)[1].replace(".zip", "") in CARS
        ]
        if len(car_zips) == 0:
            raise ValueError("No cars found, check beamng_path.")

        found = 0
        success = 0

        cars_and_configs = {}
        for car_zip_path in tqdm(car_zips, desc="Searching for cars and configs."):
            car_name = os.path.split(car_zip_path)[1].replace(".zip", "")
            with tempfile.TemporaryDirectory() as td, zipfile.ZipFile(
                car_zip_path, "r"
            ) as cz:
                cz.extractall(td)
                extracted_path = os.path.join(td, "vehicles", car_name)
                part_configs = glob.glob(os.path.join(extracted_path, "*.pc"))

                out_path = pathlib.Path(os.path.join(output_path, car_name))
                out_path.mkdir(exist_ok=True, parents=True)

                json_paths = {}
                for path in part_configs:
                    found += 1
                    # Read each dict-compatible-but-not-valid-json-file in temp dir
                    path_dict, ok = CarConfigs._try_parse_file(
                        path, extracted_path, str(out_path), verbose=verbose
                    )
                    json_paths.update(path_dict)
                    success += ok

            cars_and_configs[car_name] = json_paths

        output_fn = os.path.join(output_path, "cars_and_configs.json")
        with open(output_fn, "w") as f:
            json.dump(cars_and_configs, f)

        print(
            f"Successfully converted {success}/{found} of the found .pc files to .json."
        )
