from SapphireQuant.Core.QiList import QiList


class TickSeries(QiList):
    """
    BarSeries
    """

    def __init__(self):
        self._instrumentId = ''
        super().__init__(self)

    def get_item_by_date_time(self, date_time):
        """
        根据时间获取元素
        :param date_time:
        :return:
        """
        index = self.get_index(date_time)
        if index > -1:
            return self[index]

        return None

    def contains(self, date_time):
        """
        是否包含指定时间的Bar
        :param date_time:
        :return:
        """
        return self.first is not None and self.last is not None and self.first.date_time <= date_time <= self.last.date_time

    def clone(self):
        """
        克隆
        :return:
        """
        tick_series = TickSeries()
        for i in range(0, self.length):
            tick_series.append(self[i].clone())
        return tick_series

    def get_date_time(self, index):
        """
        获取指定index对应的Bar的begin_time
        :param index:
        :return:
        """
        if self.length > index:
            return self[index].date_time
        return None

    def get_index(self, date_time):
        """
        获取指定date_time所在的index
        :param date_time:
        :return:
        """

        if self.contains(date_time):
            if self.length == 1:
                if abs((self[0].date_time - date_time).total_seconds() * 1000) < 250.0:
                    return 0
            else:
                if self.length >= 2:
                    i = self.length - 1
                    while i > 0:
                        tick = self[i]
                        tick2 = self[i - 1]
                        if tick is not None and tick2 is not None and tick2.date_time <= date_time <= tick.date_time:
                            num = abs((date_time - tick2.date_time).total_seconds() * 1000)
                            num2 = abs((date_time - tick.date_time).total_seconds() * 1000)
                            if num2 <= num:
                                return i
                            return i - 1
                        else:
                            i = i - 1

                pass
        return 0

    def get_ago_index(self, date_time):
        """

        :param date_time:
        :return:
        """
        index = self.get_index(date_time)
        if index > -1:
            return self.length - 1 - index
        return -1

# Test Code
# begin_time = datetime.datetime(2019, 12, 1, 14, 0, 0)
# end_time = datetime.datetime(2019, 12, 1, 14, 0, 3)
# time_delta = begin_time - end_time
# print(time_delta.total_seconds())
