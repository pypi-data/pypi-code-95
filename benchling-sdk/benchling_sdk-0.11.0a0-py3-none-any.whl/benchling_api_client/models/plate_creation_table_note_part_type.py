from enum import Enum


class PlateCreationTableNotePartType(str, Enum):
    PLATE_CREATION_TABLE = "plate_creation_table"

    def __str__(self) -> str:
        return str(self.value)
