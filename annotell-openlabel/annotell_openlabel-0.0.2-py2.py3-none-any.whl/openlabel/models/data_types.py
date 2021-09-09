from dataclasses import dataclass, field
from typing import Any, List, Union


@dataclass
class DataTypeBase:
    name: str = None
    val: Any = None


@dataclass
class Boolean(DataTypeBase):
    val: bool = None

    def __post_init__(self):
        assert isinstance(self.val, bool)


@dataclass
class Num(DataTypeBase):
    val: Union[int, float] = None

    def __post_init__(self):
        assert isinstance(self.val, int) or isinstance(self.val, float)


@dataclass
class Text(DataTypeBase):
    val: str = ""

    def __post_init__(self):
        assert isinstance(self.val, str)


@dataclass
class Vec(DataTypeBase):
    val: Union[List[int], List[float]] = field(default_factory=list)

    def __post_init__(self):
        assert isinstance(self.val, list)
