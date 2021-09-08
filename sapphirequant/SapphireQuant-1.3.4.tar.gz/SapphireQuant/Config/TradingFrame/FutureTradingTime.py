import datetime

from SapphireQuant.Config.TradingDay import TradingDayHelper


class FutureTradingTime:
    """
    期货自然日交易时间
    """

    def __init__(self, instrument_id, trading_date, lst_time_slice):
        self.instrument_id = instrument_id
        self.trading_date = trading_date

        self.if_night_flag = False
        self.night_open = TradingDayHelper.get_natural_date_time(trading_date, datetime.timedelta(hours=21, minutes=0))
        self.night_close = TradingDayHelper.get_natural_date_time(trading_date, datetime.timedelta(hours=2, minutes=30))

        self.day_am_open = trading_date + datetime.timedelta(hours=9, minutes=0)
        self.day_am_rest_begin = trading_date + datetime.timedelta(hours=10, minutes=30)
        self.day_am_rest_end = trading_date + datetime.timedelta(hours=10, minutes=30)
        self.day_am_close = trading_date + datetime.timedelta(hours=11, minutes=30)
        self.day_pm_open = trading_date + datetime.timedelta(hours=13, minutes=0)
        self.day_pm_close = trading_date + datetime.timedelta(hours=15, minutes=0)

        if lst_time_slice is not None and len(lst_time_slice) > 0:
            for time_slice in lst_time_slice:
                if datetime.timedelta(hours=20) < time_slice.begin_time < datetime.timedelta(hours=23):
                    self.if_night_flag = True
                    self.night_open = TradingDayHelper.get_natural_date_time(trading_date, time_slice.begin_time)
                    self.night_close = TradingDayHelper.get_natural_date_time(trading_date, time_slice.end_time)

                if datetime.timedelta(hours=5) < time_slice.begin_time < datetime.timedelta(hours=10):
                    self.day_am_open = trading_date + time_slice.begin_time

                if datetime.timedelta(hours=10, minutes=0) < time_slice.end_time < datetime.timedelta(hours=10, minutes=20):
                    self.day_am_rest_begin = trading_date + time_slice.end_time

                if datetime.timedelta(hours=10, minutes=20) < time_slice.begin_time < datetime.timedelta(hours=10, minutes=40):
                    self.day_am_rest_end = trading_date + time_slice.begin_time

                if datetime.timedelta(hours=11, minutes=20) < time_slice.end_time < datetime.timedelta(hours=11, minutes=40):
                    self.day_am_close = trading_date + time_slice.end_time

                if datetime.timedelta(hours=12, minutes=20) < time_slice.begin_time < datetime.timedelta(hours=13, minutes=40):
                    self.day_pm_open = trading_date + time_slice.begin_time

                if datetime.timedelta(hours=14, minutes=50) < time_slice.end_time < datetime.timedelta(hours=16, minutes=0):
                    self.day_pm_close = trading_date + time_slice.end_time

        self.auction_begin = self.day_am_open + datetime.timedelta(minutes=-4)
        self.auction_end = self.day_am_open + datetime.timedelta(minutes=-1)
        self.auction_match_time = self.auction_end

    def to_string(self):
        """

        :return:
        """
        msg = '[{0}],是否有夜盘:{1}\n'.format(self.instrument_id, self.if_night_flag)
        msg += '夜盘：[0-1]\n'.format(self.night_open.stftime('%Y%m%d %H:%M:%S'), self.night_close.stftime('%Y%m%d %H:%M:%S'))
        if self.day_am_rest_begin == self.day_am_rest_end:
            msg += '上午：[0-1]\n'.format(self.day_am_open.stftime('%Y%m%d %H:%M:%S'), self.day_am_close.stftime('%Y%m%d %H:%M:%S'))
        else:
            msg += '上午：[0-1],[2-3]\n'.format(self.day_am_open.stftime('%Y%m%d %H:%M:%S'),
                                             self.day_am_rest_begin.stftime('%Y%m%d %H:%M:%S'),
                                             self.day_am_rest_end.stftime('%Y%m%d %H:%M:%S'),
                                             self.day_am_close.stftime('%Y%m%d %H:%M:%S'))
        msg += '下午：[0-1]'.format(self.day_pm_open.stftime('%Y%m%d %H:%M:%S'), self.day_pm_close.stftime('%Y%m%d %H:%M:%S'))
        return msg
