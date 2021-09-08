from enum import Enum, unique


@unique
class EnumHedgeFlag(Enum):
    投机 = 0
    套利 = 1
    套保 = 2

    def chinese_name(self):
        """

        :return:
        """
        if self == EnumHedgeFlag.投机:
            return '投机'
        elif self == EnumHedgeFlag.套利:
            return '套利'
        else:
            return '套保'
