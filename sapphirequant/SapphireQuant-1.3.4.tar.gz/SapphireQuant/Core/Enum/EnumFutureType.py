from enum import Enum, unique


@unique
class EnumFutureType(Enum):
    normal = 0
    index = 1
    reference = 2
