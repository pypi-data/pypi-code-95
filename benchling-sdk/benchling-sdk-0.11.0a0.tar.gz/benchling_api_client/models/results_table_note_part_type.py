from enum import Enum


class ResultsTableNotePartType(str, Enum):
    RESULTS_TABLE = "results_table"

    def __str__(self) -> str:
        return str(self.value)
