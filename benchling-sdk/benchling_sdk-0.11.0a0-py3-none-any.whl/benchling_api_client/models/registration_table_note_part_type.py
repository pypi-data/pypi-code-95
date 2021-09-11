from enum import Enum


class RegistrationTableNotePartType(str, Enum):
    REGISTRATION_TABLE = "registration_table"

    def __str__(self) -> str:
        return str(self.value)
