from enum import Enum


class PlateSchemaType(str, Enum):
    PLATE = "plate"

    def __str__(self) -> str:
        return str(self.value)
