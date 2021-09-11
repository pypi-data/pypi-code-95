from enum import Enum


class ExternalFileNotePartType(str, Enum):
    EXTERNAL_FILE = "external_file"

    def __str__(self) -> str:
        return str(self.value)
