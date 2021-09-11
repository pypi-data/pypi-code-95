from enum import Enum


class EntryUpdatedFieldsEventEventType(str, Enum):
    V2_ENTRYUPDATEDFIELDS = "v2.entry.updated.fields"

    def __str__(self) -> str:
        return str(self.value)
