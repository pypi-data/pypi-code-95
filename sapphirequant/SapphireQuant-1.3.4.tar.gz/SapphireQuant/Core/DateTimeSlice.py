import datetime


class DateTimeSlice:
    """
    日期时间间隔
    """
    def __init__(self):
        self.__begin = datetime.datetime
        self.__end = datetime.datetime

    @property
    def begin_time(self):
        return self.__begin

    @begin_time.setter
    def begin_time(self, value):
        self.__begin = value

    @property
    def end_time(self):
        return self.__end

    @end_time.setter
    def end_time(self, value):
        self.__end = value

    @property
    def duration(self):
        return self.__end - self.__begin
