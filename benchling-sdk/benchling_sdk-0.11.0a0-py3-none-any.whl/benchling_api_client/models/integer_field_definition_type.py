from enum import Enum


class IntegerFieldDefinitionType(str, Enum):
    INTEGER = "integer"

    def __str__(self) -> str:
        return str(self.value)
