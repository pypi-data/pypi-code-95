import enum
from enum import Enum, unique


@unique
class EnumExchange(enum.IntEnum):
    上证所 = 0
    深交所 = 1
    中金所 = 2
    上期所 = 3
    大商所 = 4
    郑商所 = 5
    新交所 = 6
    未知 = 7
    火币 = 8
    欧易 = 9  # OKEX
    币安 = 10
