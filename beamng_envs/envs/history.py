from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class History:
    time_key: str = "time_s"
    car_state_key: str = "car_state"
    step_key: str = "time_pts"
    other_keys: List[str] = field(default_factory=lambda: [])

    _history: Dict[str, List[Any]] = field(init=False, repr=False)

    def __post_init__(self):
        self.reset()

    def __getitem__(self, item):
        return self._history[item]

    def __len__(self):
        return len(self._history[self.time_key])

    @property
    def __dict__(self):
        return self._history

    @property
    def keys(self):
        return [self.time_key, self.car_state_key, self.step_key] + self.other_keys

    def append(self, items: Dict[str, Any]):
        for k, v in items.items():
            self._history[k].append(v)

    def reset(self):
        self._history = {k: [] for k in self.keys}
