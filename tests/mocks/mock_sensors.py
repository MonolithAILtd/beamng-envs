from typing import Dict, Any, List, Callable
from unittest.mock import MagicMock


class MockSensor(MagicMock):
    data: Dict[str, Any]


class MockStateSensor(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: Dict[str, Any] = {
            "rotation": [0, 0, 0],
            "front": [0, 0, 0],
            "vel": [0, 0, 0],
            "up": [0, 0, 0],
            "dir": [0, 0, 0],
            "pos": [0, 0, 0],
        }
        self.__getitem__ = lambda obj, item: self.data["pos"]


class MockDamageSensor(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: Dict[str, Any] = {"damage": {"damage": 0}}
        self.__getitem__ = lambda obj, item: self.data["damage"]


class MockSensors(MagicMock):
    sensors: Dict[str, MockSensor]
    _step: int = 0
    _loc: List[float]
    __getitem__: Callable

    def _set_loc(self):
        if self._step == 0:
            self._loc = [-408.4, 260.23, 25.423]
        if self._step == 2:
            self._loc = [47.0, 256.0, 28.0]
        if self._step == 4:
            self._loc = [393.0, -130.0, 34.0]
        if self._step == 6:
            self._loc = [-12.0, -65.0, 29.0]
        if self._step == 8:
            self._loc = [-220.0, 368.0, 27.0]
        if self._step == 10:
            self._loc = [-413.0, 467.0, 34.0]
        if self._step == 12:
            self._loc = [-402.0, 244.0, 25.0]

    def poll(self) -> None:
        self._set_loc()
        self._step += 1
        self.sensors = {"state": MockSensor(), "damage": MockSensor()}
        self.sensors["state"].data = {
            "rotation": [0, 0, 0],
            "front": [0, 0, 0],
            "vel": [0, 0, 0],
            "up": [0, 0, 0],
            "dir": [0, 0, 0],
            "pos": self._loc,
        }

        # Set MockSensors to always return mock state sensor (__getitem__ is patched here rather than defined in its
        # own method to avoid getting overloaded in creation of the MagicMock object).
        self.__getitem__ = lambda obj, item: self.sensors["state"]
