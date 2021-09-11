from enum import Enum


class DropdownFieldDefinitionType(str, Enum):
    DROPDOWN = "dropdown"

    def __str__(self) -> str:
        return str(self.value)
