from enum import Enum


class UserValidationValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    PARTIALLY_VALID = "PARTIALLY_VALID"

    def __str__(self) -> str:
        return str(self.value)
