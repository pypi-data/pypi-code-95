from enum import Enum


class AssayRunUpdatedFieldsEventEventType(str, Enum):
    V2_ASSAYRUNUPDATEDFIELDS = "v2.assayRun.updated.fields"

    def __str__(self) -> str:
        return str(self.value)
