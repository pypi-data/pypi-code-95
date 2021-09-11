from enum import Enum


class MixtureMeasurementUnits(str, Enum):
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"
    G = "g"
    KG = "kg"
    UNITS = "Units"

    def __str__(self) -> str:
        return str(self.value)
