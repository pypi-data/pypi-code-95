from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Filter:
    field: str
    filter: Callable[[Any], bool]
