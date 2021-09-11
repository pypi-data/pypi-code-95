from enum import Enum


class OligoNucleotideType(str, Enum):
    DNA = "DNA"
    RNA = "RNA"

    def __str__(self) -> str:
        return str(self.value)
