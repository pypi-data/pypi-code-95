from enum import Enum


class RequestSchemaType(str, Enum):
    REQUEST = "request"

    def __str__(self) -> str:
        return str(self.value)
