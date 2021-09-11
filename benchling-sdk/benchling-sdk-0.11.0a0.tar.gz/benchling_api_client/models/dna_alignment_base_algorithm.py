from enum import Enum


class DnaAlignmentBaseAlgorithm(str, Enum):
    MAFFT = "mafft"
    CLUSTALO = "clustalo"

    def __str__(self) -> str:
        return str(self.value)
