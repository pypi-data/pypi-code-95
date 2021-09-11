from enum import Enum


class DropdownOptionsArchiveReason(str, Enum):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)
