from enum import Enum


class MetadataCreatorsItemPersonOrOrgType(str, Enum):
    PERSONAL = "personal"
    ORGANISATIONAL = "organisational"

    def __str__(self) -> str:
        return str(self.value)
