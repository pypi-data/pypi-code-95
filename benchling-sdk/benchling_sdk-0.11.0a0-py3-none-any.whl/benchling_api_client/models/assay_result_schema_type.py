from enum import Enum


class AssayResultSchemaType(str, Enum):
    ASSAY_RESULT = "assay_result"

    def __str__(self) -> str:
        return str(self.value)
