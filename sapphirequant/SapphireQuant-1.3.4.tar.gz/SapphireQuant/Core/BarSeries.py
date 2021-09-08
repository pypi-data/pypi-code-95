from SapphireQuant.Core.QiList import QiList


class BarSeries(QiList):
    """
    BarSeries
    """

    def __init__(self):
        self._instrumentId = ''
        super().__init__(self)

    @property
    def instrument_id(self):
        """
        合约编号
        :return:
        """
        return self._instrumentId

    @instrument_id.setter
    def instrument_id(self, value):
        self._instrumentId = value

    def get_item_by_date_time(self, date_time):
        """
        根据时间获取元素
        :param date_time:
        :return:
        """
        count = self.length
        for i in range(0, count):
            bar = self[i]
            if bar.begin_time <= date_time < bar.end_time:
                return bar

        return None

    def get_item_by_index_bar_data(self, index, bar_data):
        """
        根据时间获取元素
        :param index:
        :param bar_data:
        :return:
        """
        if self.length <= index or index < 0:
            return 0.0
        return self[index][bar_data]

    def get_item_by_date_time_bar_data(self, date_time, bar_data):
        """
        根据时间获取元素
        :param date_time:
        :param bar_data:
        :return:
        """
        bar = self.get_item_by_date_time(date_time)
        if bar is not None:
            return bar[bar_data]
        return 0.0

    @property
    def sum_volume(self):
        """
        volume求和
        :return:
        """
        num = 0.0
        for i in range(0, self.length):
            num += self[i].volume
        return num

    @property
    def sum_turnover(self):
        """
        volume求和
        :return:
        """
        num = 0.0
        for i in range(0, self.length):
            num += self[i].turnover
        return num

    @property
    def high(self):
        """
        最高价序列
        :return:
        """
        result = None
        try:
            count = self.length
            data_series = []
            if count > 0:
                for i in range(0, count):
                    data_series.append(self[i].high)
                result = data_series
        except Exception as e:
            result = None
            print(str(e))
        return result

    @property
    def open(self):
        """
        最高价序列
        :return:
        """
        result = None
        try:
            count = self.length
            data_series = []
            if count > 0:
                for i in range(0, count):
                    data_series.append(self[i].open)
                result = data_series
        except Exception as e:
            result = None
            print(str(e))
        return result

    @property
    def low(self):
        """
        最高价序列
        :return:
        """
        result = None
        try:
            count = self.length
            data_series = []
            if count > 0:
                for i in range(0, count):
                    data_series.append(self[i].low)
                result = data_series
        except Exception as e:
            result = None
            print(str(e))
        return result

    @property
    def close(self):
        """
        最高价序列
        :return:
        """
        result = None
        try:
            count = self.length
            data_series = []
            if count > 0:
                for i in range(0, count):
                    data_series.append(self[i].close)
                result = data_series
        except Exception as e:
            result = None
            print(str(e))
        return result

    @property
    def volume(self):
        """
        最高价序列
        :return:
        """
        result = None
        try:
            count = self.length
            data_series = []
            if count > 0:
                for i in range(0, count):
                    data_series.append(self[i].volume)
                result = data_series
        except Exception as e:
            result = None
            print(str(e))
        return result

    @property
    def turnover_series(self):
        """
        最高价序列
        :return:
        """
        result = None
        try:
            count = self.length
            data_series = []
            if count > 0:
                for i in range(0, count):
                    data_series.append(self[i].turnover)
                result = data_series
        except Exception as e:
            result = None
            print(str(e))
        return result

    def contains(self, date_time):
        """
        是否包含指定时间的Bar
        :param date_time:
        :return:
        """
        return self.first is not None and self.last is not None and self.first.begin_time <= date_time <= self.last.end_time

    def clone(self):
        """
        克隆
        :return:
        """
        bar_series = BarSeries()
        for i in range(0, self.length):
            bar_series.append(self[i].clone())
        return bar_series

    def get_date_time(self, index):
        """
        获取指定index对应的Bar的begin_time
        :param index:
        :return:
        """
        if self.length > index:
            return self[index].begin_time
        return None

    def get_index(self, date_time):
        """
        获取指定date_time所在的index
        :param date_time:
        :return:
        """
        count = self.length
        result = -1
        if self.contains(date_time):
            for i in range(0, count):
                if self[i].begin_time <= date_time < self[i].end_time:
                    result = i
        return result

    def get_index_by_option(self):
        """
        pass
        """
        pass



bar_series = BarSeries()
bar_series.append(['1'])