from enum import Enum


class BoxCreationTableNotePartType(str, Enum):
    BOX_CREATION_TABLE = "box_creation_table"

    def __str__(self) -> str:
        return str(self.value)
