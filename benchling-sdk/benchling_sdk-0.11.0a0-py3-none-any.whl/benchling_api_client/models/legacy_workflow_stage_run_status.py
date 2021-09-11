from enum import Enum


class LegacyWorkflowStageRunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    DISCARDED = "DISCARDED"
    INITIALIZED = "INITIALIZED"

    def __str__(self) -> str:
        return str(self.value)
