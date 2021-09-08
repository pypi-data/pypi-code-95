from enum import Enum, unique


@unique
class EnumPositionType(Enum):
    今仓 = 0
    昨仓 = 1

    def chinese_name(self):
        """

        :return:
        """
        if self == EnumPositionType.今仓:
            return '今仓'
        else:
            return '昨仓'
