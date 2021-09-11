from enum import Enum


class LocationSchemaType(str, Enum):
    LOCATION = "location"

    def __str__(self) -> str:
        return str(self.value)
