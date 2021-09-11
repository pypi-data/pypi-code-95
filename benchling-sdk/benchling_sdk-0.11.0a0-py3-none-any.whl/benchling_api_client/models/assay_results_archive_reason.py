from enum import Enum


class AssayResultsArchiveReason(str, Enum):
    MADE_IN_ERROR = "Made in error"
    ARCHIVED = "Archived"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)
