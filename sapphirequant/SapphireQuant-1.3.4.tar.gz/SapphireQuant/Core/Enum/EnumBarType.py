import enum
from enum import Enum, unique


@unique
class EnumBarType(enum.IntEnum):
    tick = 0
    second = 1
    minute = 2
    hour = 3
    day = 4
    week = 5
    month = 6
    year = 7
    night_am_pm = 8