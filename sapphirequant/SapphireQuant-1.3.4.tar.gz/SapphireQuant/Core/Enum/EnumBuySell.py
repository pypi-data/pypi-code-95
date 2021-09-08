from enum import Enum, unique


@unique
class EnumBuySell(Enum):
    买入 = 0
    卖出 = 1

    def chinese_name(self):
        """

        :return:
        """
        if self == EnumBuySell.买入:
            return '买入'
        else:
            return '卖出'
