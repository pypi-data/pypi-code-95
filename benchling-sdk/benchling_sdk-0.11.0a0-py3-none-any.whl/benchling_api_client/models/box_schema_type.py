from enum import Enum


class BoxSchemaType(str, Enum):
    BOX = "box"

    def __str__(self) -> str:
        return str(self.value)
