from enum import Enum, unique


@unique
class EnumRestoration(Enum):
    不复权 = 0
    前复权 = 1
    后复权 = 2
