from enum import Enum


class AsyncTaskStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)
