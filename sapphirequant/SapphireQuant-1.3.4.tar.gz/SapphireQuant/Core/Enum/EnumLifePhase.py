from enum import Enum, unique


@unique
class EnumLifePhase(Enum):
    未上市 = 48
    上市 = 49
    停牌 = 50
    到期 = 51
