from enum import Enum


class AutomationFileStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
