from __future__ import annotations

from .missing import MISSING
from .exceptions import MissingValueException


class Field:
    def __init__(self, default=MISSING, default_factory=MISSING, optional: bool = False):
        num_of_options = sum((default is not MISSING, default_factory is not MISSING, optional))
        if num_of_options > 1:
            raise ValueError("default, default_factory and optional are mutually exclusive parameters.")
        self.default = default
        self.default_factory = default_factory
        self.optional = optional

    def parse(self, dataval: any):
        raise NotImplementedError

    def get_default(self, path: str):
        if self.default is not MISSING:
            return self.default
        elif self.default_factory is not MISSING:
            return self.default_factory()
        elif self.optional:
            return MISSING
        else:
            raise MissingValueException(f"Missing value: {path}")
