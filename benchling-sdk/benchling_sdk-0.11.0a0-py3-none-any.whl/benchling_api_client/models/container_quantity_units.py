from enum import Enum


class ContainerQuantityUnits(str, Enum):
    PL = "pL"
    NL = "nL"
    UL = "uL"
    ML = "mL"
    L = "L"
    PG = "pg"
    NG = "ng"
    UG = "ug"
    MG = "mg"
    G = "g"
    KG = "kg"
    ITEMS = "items"
    UNITS = "units"

    def __str__(self) -> str:
        return str(self.value)
