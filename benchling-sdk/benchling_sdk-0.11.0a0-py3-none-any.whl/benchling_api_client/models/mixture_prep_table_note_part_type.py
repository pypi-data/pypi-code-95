from enum import Enum


class MixturePrepTableNotePartType(str, Enum):
    MIXTURE_PREP_TABLE = "mixture_prep_table"

    def __str__(self) -> str:
        return str(self.value)
