from enum import Enum


class EntryCreatedEventEventType(str, Enum):
    V2_ENTRYCREATED = "v2.entry.created"

    def __str__(self) -> str:
        return str(self.value)
