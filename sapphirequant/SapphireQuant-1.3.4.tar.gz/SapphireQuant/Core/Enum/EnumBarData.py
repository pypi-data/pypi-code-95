
import enum


@enum.unique
class EnumBarData(enum.Enum):
    close = 0
    open = 1
    high = 2
    low = 3
    volume = 4
    turnover = 5
