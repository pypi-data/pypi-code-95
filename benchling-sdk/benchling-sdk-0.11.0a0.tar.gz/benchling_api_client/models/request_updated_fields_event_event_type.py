from enum import Enum


class RequestUpdatedFieldsEventEventType(str, Enum):
    V2_REQUESTUPDATEDFIELDS = "v2.request.updated.fields"

    def __str__(self) -> str:
        return str(self.value)
