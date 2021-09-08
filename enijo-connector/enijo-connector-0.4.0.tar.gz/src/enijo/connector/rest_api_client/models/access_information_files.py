from enum import Enum


class AccessInformationFiles(str, Enum):
    PUBLIC = "public"
    RESTRICTED = "restricted"

    def __str__(self) -> str:
        return str(self.value)
