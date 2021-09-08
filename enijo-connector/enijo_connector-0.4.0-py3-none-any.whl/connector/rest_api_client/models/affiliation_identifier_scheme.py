from enum import Enum


class AffiliationIdentifierScheme(str, Enum):
    ISNI = "isni"
    ROR = "ror"

    def __str__(self) -> str:
        return str(self.value)
