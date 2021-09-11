from enum import Enum


class ContainerVolumeUnits(str, Enum):
    PL = "pL"
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"

    def __str__(self) -> str:
        return str(self.value)
