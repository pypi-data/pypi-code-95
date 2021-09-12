from dataclasses import dataclass
from datetime import datetime
from typing import Type, TypeVar

from ..utils.parsers.dataclasses import pick_into_dataclass

T = TypeVar("T", bound="Timestamp")  # pylint: disable = C0103


@dataclass
class Timestamp:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    @classmethod
    def parse(cls: Type[T], dt: datetime) -> T:  # pylint: disable = C0103
        return pick_into_dataclass(cls, dt)

    @classmethod
    def now(cls: Type[T]) -> T:
        return cls.parse(datetime.now())
