from enum import Enum


class SimpleNotePartType(str, Enum):
    TEXT = "text"
    CODE = "code"
    LIST_BULLET = "list_bullet"
    LIST_NUMBER = "list_number"

    def __str__(self) -> str:
        return str(self.value)
