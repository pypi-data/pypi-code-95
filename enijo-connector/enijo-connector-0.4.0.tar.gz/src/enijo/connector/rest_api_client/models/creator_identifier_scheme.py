from enum import Enum


class CreatorIdentifierScheme(str, Enum):
    ORCID = "orcid"
    GND = "gnd"
    ISNI = "isni"
    ROR = "ror"

    def __str__(self) -> str:
        return str(self.value)
