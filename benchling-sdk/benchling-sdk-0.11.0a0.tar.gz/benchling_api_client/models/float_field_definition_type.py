from enum import Enum


class FloatFieldDefinitionType(str, Enum):
    FLOAT = "float"

    def __str__(self) -> str:
        return str(self.value)
