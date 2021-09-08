import datetime


class TimeSlice:
    """
    时间区间
    """
    def __init__(self, begin_time=datetime.timedelta(), end_time=datetime.timedelta()):
        self._begin_time = begin_time
        self._end_time = end_time
        self._normal = True

    @property
    def begin_time(self) -> datetime.timedelta:
        """

        :return:
        """
        return self._begin_time

    @begin_time.setter
    def begin_time(self, value):
        self._begin_time = value
        self._normal = (self._begin_time.total_seconds() < self._end_time.total_seconds())

    @property
    def end_time(self) -> datetime.timedelta:
        """

        :return:
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        self._end_time = value
        self._normal = (self._begin_time.total_seconds() < self._end_time.total_seconds())

    @property
    def duration(self) -> datetime.timedelta:
        """

        :return:
        """
        return self._end_time - self._begin_time

    @property
    def normal(self) -> bool:
        """

        :return:
        """
        return self._normal

    def contains(self, sp) -> bool:
        """

        :param sp:
        :return:
        """
        if not self._normal:
            return (self._begin_time.total_seconds() <= sp.total_seconds()) | (sp.total_seconds() <= self._end_time.total_seconds())
        return (self._begin_time.total_seconds() <= sp.total_seconds()) & (sp.total_seconds() <= self._end_time.total_seconds())

    def to_string(self):
        """

        :return:
        """
        return "[" + str(self._begin_time) + "-" + str(self._end_time) + "]"


# time_slice = TimeSlice()
# print(str(time_slice.begin_time))
# print(str(time_slice.end_time))
# time_slice.begin_time = datetime.timedelta(seconds=5)
# time_slice.end_time = datetime.timedelta(seconds=6)
# print(str(time_slice.begin_time))
# print(str(time_slice.end_time))
# print(str(time_slice.duration))
# print(time_slice.to_string())
