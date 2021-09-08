from enum import Enum, unique


@unique
class EnumPositionDirection(Enum):
    多头 = 0
    空头 = 1
    净持仓 = 2
    备兑 = 3

    def chinese_name(self):
        """

        :return:
        """
        if self == EnumPositionDirection.多头:
            return '多头'
        elif self == EnumPositionDirection.空头:
            return '空头'
        elif self == EnumPositionDirection.净持仓:
            return '净持仓'
        else:
            return '备兑'
