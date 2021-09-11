from enum import Enum


class EntityRegisteredEventEventType(str, Enum):
    V2_ENTITYREGISTERED = "v2.entity.registered"

    def __str__(self) -> str:
        return str(self.value)
