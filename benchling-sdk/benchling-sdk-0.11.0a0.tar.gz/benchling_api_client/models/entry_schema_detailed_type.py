from enum import Enum


class EntrySchemaDetailedType(str, Enum):
    ENTRY = "entry"

    def __str__(self) -> str:
        return str(self.value)
