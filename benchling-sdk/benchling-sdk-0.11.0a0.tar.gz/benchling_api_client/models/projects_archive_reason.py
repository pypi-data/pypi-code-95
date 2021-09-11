from enum import Enum


class ProjectsArchiveReason(str, Enum):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)
