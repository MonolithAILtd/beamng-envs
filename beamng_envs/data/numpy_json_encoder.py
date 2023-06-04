from json import JSONEncoder
from typing import Any, List, Union

import numpy as np


class NumpyJSONEncoder(JSONEncoder):
    """Encoder for numpy arrays and types -> json"""

    def default(self, obj) -> Union[List[Any], float, int]:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int16, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, (np.float16, np.float32, np.float64)):
            return float(obj)

        return JSONEncoder.default(self, obj)
