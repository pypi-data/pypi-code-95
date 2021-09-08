import datetime


class QiDataDirectory:
    """
    目录配置
    """
    def __init__(self):
        self.__trading_day = datetime.date
        self.__future_tick = ""
        self.__future_tick_cache = ""
        self.__future_min = ""
        self.__future_day = ""

    @property
    def trading_day(self):
        """

        :return:
        """
        return self.__trading_day

    @trading_day.setter
    def trading_day(self, value):
        self.__trading_day = value

    @property
    def future_tick(self):
        return self.__future_tick

    @future_tick.setter
    def future_tick(self, value):
        self.__future_tick = value

    @property
    def future_tick_cache(self):
        return self.__future_tick_cache

    @future_tick_cache.setter
    def future_tick_cache(self, value):
        self.__future_tick_cache = value

    @property
    def future_min(self):
        return self.__future_min

    @future_min.setter
    def future_min(self, value):
        self.__future_min = value

    @property
    def future_day(self):
        return self.__future_day

    @future_day.setter
    def future_day(self, value):
        self.__future_day = value
