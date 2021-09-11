from enum import Enum


class TealLevel(Enum):
    none = 0  # Prints no message, not even errors
    error = 1
    warning = 2
    info = 3  # Default
    verbose = 4
    debug = 5
