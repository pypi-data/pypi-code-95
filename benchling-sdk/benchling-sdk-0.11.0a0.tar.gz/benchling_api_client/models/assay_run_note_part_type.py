from enum import Enum


class AssayRunNotePartType(str, Enum):
    ASSAY_RUN = "assay_run"

    def __str__(self) -> str:
        return str(self.value)
