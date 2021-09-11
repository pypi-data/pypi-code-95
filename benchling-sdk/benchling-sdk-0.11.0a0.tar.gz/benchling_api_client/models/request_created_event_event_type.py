from enum import Enum


class RequestCreatedEventEventType(str, Enum):
    V2_REQUESTCREATED = "v2.request.created"

    def __str__(self) -> str:
        return str(self.value)
