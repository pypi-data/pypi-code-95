from enum import Enum, unique


@unique
class EnumStrategyWorkMode(Enum):
    live = 0
    simulate = 1
