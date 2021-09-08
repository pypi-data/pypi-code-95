from enum import Enum, unique


@unique
class EnumProductClass(Enum):
    future = 1  # 期货
    option = 2  # 期货期权
    combination = 3  # 组合
    spot = 4  # 即期
    efp = 5  # 期转现
    spot_option = 6  # 现货期权
