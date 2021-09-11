from enum import Enum


class TableNotePartType(str, Enum):
    TABLE = "table"

    def __str__(self) -> str:
        return str(self.value)
