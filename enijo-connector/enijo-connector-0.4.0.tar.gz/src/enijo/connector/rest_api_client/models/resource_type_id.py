from enum import Enum


class ResourceTypeId(str, Enum):
    IMAGE = "image"
    DATASET = "dataset"

    def __str__(self) -> str:
        return str(self.value)
