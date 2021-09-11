from enum import Enum


class ContainerSchemaType(str, Enum):
    CONTAINER = "container"

    def __str__(self) -> str:
        return str(self.value)
