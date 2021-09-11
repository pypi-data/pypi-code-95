from enum import Enum


class AssayRunValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"

    def __str__(self) -> str:
        return str(self.value)
