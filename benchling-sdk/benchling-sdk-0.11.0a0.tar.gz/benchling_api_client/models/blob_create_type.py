from enum import Enum


class BlobCreateType(str, Enum):
    RAW_FILE = "RAW_FILE"
    VISUALIZATION = "VISUALIZATION"

    def __str__(self) -> str:
        return str(self.value)
