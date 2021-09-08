from dataclasses import dataclass
from typing import Callable


@dataclass
class Cell:
    field: str
    mode: Callable or int
