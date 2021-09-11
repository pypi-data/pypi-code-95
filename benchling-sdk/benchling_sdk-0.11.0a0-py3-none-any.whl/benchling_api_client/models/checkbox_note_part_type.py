from enum import Enum


class CheckboxNotePartType(str, Enum):
    LIST_CHECKBOX = "list_checkbox"

    def __str__(self) -> str:
        return str(self.value)
