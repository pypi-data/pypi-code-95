from enum import Enum, unique


@unique
class EnumOpenClose(Enum):
    开仓 = 0
    平仓 = 1
    强平 = 2
    平今 = 3
    平昨 = 4
    强减 = 5
    本地强平 = 6

    def chinese_name(self):
        """
        中文名称
        :return:
        """
        if self == EnumOpenClose.开仓:
            return '开仓'
        elif self == EnumOpenClose.平仓:
            return '平仓'
        elif self == EnumOpenClose.强平:
            return '强平'
        elif self == EnumOpenClose.平今:
            return '平今'
        elif self == EnumOpenClose.平昨:
            return '平昨'
        elif self == EnumOpenClose.强减:
            return '强减'
        else:
            return '本地强平'