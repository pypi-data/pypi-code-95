from enum import Enum


class EntitySchemaContainableType(str, Enum):
    NONE = "NONE"
    ENTITY = "ENTITY"
    BATCH = "BATCH"

    def __str__(self) -> str:
        return str(self.value)
