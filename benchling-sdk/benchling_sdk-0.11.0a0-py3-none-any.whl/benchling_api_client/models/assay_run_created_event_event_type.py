from enum import Enum


class AssayRunCreatedEventEventType(str, Enum):
    V2_ASSAYRUNCREATED = "v2.assayRun.created"

    def __str__(self) -> str:
        return str(self.value)
