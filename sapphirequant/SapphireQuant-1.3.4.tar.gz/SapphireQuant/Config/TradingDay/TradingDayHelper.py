
import datetime
import os
import sys


class TradingDayHelper:
    """
    交易日帮助类
    """
    _days = None
    IsLoaded = False

    @staticmethod
    def trading_days():
        """
        交易日
        :return:
        """
        if TradingDayHelper._days is None:
            TradingDayHelper.get_all_china_trading_days()
        return TradingDayHelper._days

    @staticmethod
    def get_all_china_trading_days():
        """
        获取中国交易日列表
        """
        TradingDayHelper._days = []
        trading_calendar_dir = os.path.join(sys.modules['ROOT_DIR'], 'Profiles', 'TradingCalendar')
        trading_calendar_files = os.listdir(trading_calendar_dir)  # 列出文件夹下所有的目录与文件
        for i in range(0, len(trading_calendar_files)):
            trading_day_file = os.path.join(trading_calendar_dir, trading_calendar_files[i])
            if os.path.isfile(trading_day_file):
                for line in open(trading_day_file, "r"):  # 设置文件对象并读取每一行文件
                    n_trading_date = int(line)
                    year = n_trading_date // 10000
                    month = n_trading_date % 10000 // 100
                    day = n_trading_date % 100
                    trading_date = datetime.datetime(year, month, day)
                    TradingDayHelper._days.append(trading_date)
        TradingDayHelper.IsLoaded = True

    @staticmethod
    def get_trading_days(begin_date, end_date):
        """
        获取日期区间内的所有交易日
        :param begin_date:
        :param end_date:
        :return:
        """
        list_get_trading_day = []
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        trading_days = TradingDayHelper.trading_days()
        for trading_day in trading_days:
            if (trading_day >= begin_date) & (trading_day <= end_date):
                list_get_trading_day.append(trading_day)
        return list_get_trading_day

    @staticmethod
    def get_natural_date_time(trading_date, time_span):
        """
        根据交易日和时间切片生成自然日时间
        :param trading_date:
        :param time_span:
        :return:
        """
        natural_time = trading_date + time_span
        hours = natural_time.hour
        if hours <= 6:
            natural_time = TradingDayHelper.get_pre_trading_day(trading_date) + datetime.timedelta(days=1) + time_span
        elif hours >= 16:
            natural_time = TradingDayHelper.get_pre_trading_day(trading_date) + time_span
        return natural_time

    @staticmethod
    def get_next_trading_day(date, n=1):
        """
        往后回溯n个交易日
        :param date:
        :param n:
        :return:
        """
        date = datetime.datetime(date.year, date.month, date.day)
        trading_days = TradingDayHelper.trading_days()
        index = -1
        if date in trading_days:
            index = trading_days.index(date)
        if index > -1:
            index_next = index + n
            index_next = min(len(trading_days) - 1, index_next)
            return trading_days[index_next]
        return TradingDayHelper.get_first_trading_day(date)

    @staticmethod
    def get_pre_trading_day(date, n=1):
        """
        往前回溯n个交易日
        :param date:交易日
        :param n:回溯天数
        :return:
        """
        date = datetime.datetime(date.year, date.month, date.day)
        trading_days = TradingDayHelper.trading_days()
        if date in trading_days:
            index = trading_days.index(date)
        else:
            date = TradingDayHelper.get_last_trading_day(date)
            index = trading_days.index(date)
            index = index + 1  # 非交易日的情况 默认加一天
        if index > n:
            index_next = index - n
            index_next = max(0, index_next)
            return trading_days[index_next]
        return TradingDayHelper.get_last_trading_day(date)

    @staticmethod
    def get_first_trading_day(date):
        """
        获取大于等于日期的第一个交易日
        :param date:
        :return:
        """
        date = datetime.datetime(date.year, date.month, date.day)
        for i in range(0, 20):
            if TradingDayHelper.is_china_trading_day(date):
                return date

            date = date + datetime.timedelta(days=1)

    @staticmethod
    def get_last_trading_day(date):
        """
        获取小于等于日期的最后一个交易日
        :param date:
        :return:
        """
        date = datetime.datetime(date.year, date.month, date.day)
        for i in range(0, 20):
            if TradingDayHelper.is_china_trading_day(date):
                return date

            date = date + datetime.timedelta(days=-1)

    @staticmethod
    def get_trading_day_count(begin_date, end_date):
        """
        获取交易区间的交易日个数，是闭区间，包含头尾的
        :param begin_date:
        :param end_date:
        :return:
        """
        trading_days = TradingDayHelper.trading_days()
        begin_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_date = TradingDayHelper.get_last_trading_day(end_date)
        begin_index = trading_days.index(begin_date)
        end_index = trading_days.index(end_date)
        count = 0
        if begin_index <= end_index:
            count = end_index - begin_index + 1
        return count

    @staticmethod
    def is_china_trading_day(date):
        """
        是否为中国交易日
        :param date:
        :return:
        """
        date = datetime.datetime(date.year, date.month, date.day)
        trading_days = TradingDayHelper.trading_days()
        if date not in trading_days:
            return False
        return True

# begin_date_test = datetime.datetime(2019, 4, 1)
# end_date_test = datetime.datetime(2019, 10, 1)
# next_trading_day = TradingDayHelper.get_next_trading_day(end_date_test)
# pre_trading_day = TradingDayHelper.get_pre_trading_day(end_date_test)
# first_trading_day = TradingDayHelper.get_first_trading_day(end_date_test)
# last_trading_day = TradingDayHelper.get_last_trading_day(end_date_test)
# trading_day_count = TradingDayHelper.get_trading_day_count(begin_date_test, end_date_test)
# print(next_trading_day.strftime('%Y/%m/%d'))
# print("pre_trading_day"+pre_trading_day.strftime('%Y/%m/%d'))
# print(first_trading_day.strftime('%Y/%m/%d'))
# print(last_trading_day.strftime('%Y/%m/%d'))
# print(str(trading_day_count))
# for a in data:
#     print(a.strftime('%Y/%m/%d'))
