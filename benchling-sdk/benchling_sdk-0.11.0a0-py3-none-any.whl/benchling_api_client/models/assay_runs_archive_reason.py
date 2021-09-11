from enum import Enum


class AssayRunsArchiveReason(str, Enum):
    ARCHIVED = "Archived"
    MADE_IN_ERROR = "Made in error"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)
