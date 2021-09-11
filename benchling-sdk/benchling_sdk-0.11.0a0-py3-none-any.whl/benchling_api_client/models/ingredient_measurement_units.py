from enum import Enum


class IngredientMeasurementUnits(str, Enum):
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"
    MG = "mg"
    G = "g"
    UNITS = "Units"

    def __str__(self) -> str:
        return str(self.value)
