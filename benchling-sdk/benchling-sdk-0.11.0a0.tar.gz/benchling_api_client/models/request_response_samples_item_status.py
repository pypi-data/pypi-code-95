from enum import Enum


class RequestResponseSamplesItemStatus(str, Enum):
    COMPLETED = "COMPLETED"
    DISCARDED = "DISCARDED"

    def __str__(self) -> str:
        return str(self.value)
