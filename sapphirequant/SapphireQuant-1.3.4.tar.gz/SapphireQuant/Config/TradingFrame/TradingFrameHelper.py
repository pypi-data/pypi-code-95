import datetime

from SapphireQuant.Core.TimeSlice import TimeSlice


class TradingFrameHelper:
    """
    交易框架帮助
    """
    @staticmethod
    def parse_date(str_date: str) -> datetime.datetime:
        """

        :param str_date:
        :return:
        """
        year = int(str_date[0:4])
        month = int(str_date[4:6])
        day = int(str_date[6:])
        date = datetime.datetime(year, month, day)
        return date

    @staticmethod
    def parse_time_slice(str_slice: str) -> []:
        """

        :param str_slice:
        :return:
        """
        all_slice = []
        str_slice_arr = str_slice.split(',')
        count = len(str_slice_arr) / 2
        for i in range(int(count)):
            time_slice = TimeSlice()
            time_slice.begin_time = TradingFrameHelper.str_pares_timedelta(str_slice_arr[i * 2])
            time_slice.end_time = TradingFrameHelper.str_pares_timedelta(str_slice_arr[i * 2 + 1])

            all_slice.append(time_slice)
        return all_slice

    @staticmethod
    def str_pares_timedelta(str_timedelta):
        """

        :param str_timedelta:
        :return:
        """
        str_timedelta_arr = str_timedelta.split(':')
        if len(str_timedelta_arr) == 3:
            hour = int(str_timedelta_arr[0])
            minute = int(str_timedelta_arr[1])
            second = int(str_timedelta_arr[2])
        else:
            hour = int(str_timedelta_arr[0])
            minute = int(str_timedelta_arr[1])
            second = 0

        return datetime.timedelta(hours=hour, minutes=minute, seconds=second)

# str_date = '20190808'
# TradingFrameHelper.parse_date(str_date)
