from enum import Enum
from typing import Any


class ArmType(Enum):
    FULL_ARM = 0
    NIGHT_ARM = 1
    UNKNOWN = 2
    DISARMED = 3

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


class DeviceType(Enum):
    UNKNOWN = -1
    HUB = 1
    DOORWINDOWSENSOR = 2
    PANEL = 14
    SMOKEALARM = 16
    SIREN = 24
    CAMERA = 38
    ZWAVECONTROLLER = 116
    ACCESSCHIP = 201

    @classmethod
    def _missing_(cls, value: Any):
        return DeviceType.UNKNOWN

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


class EventType(Enum):
    UNKNOWN = -1
    ARM = 39
    DISARM = 40
    NIGHTARM = 57

    @classmethod
    def _missing_(cls, value: Any):
        return EventType.UNKNOWN

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)
