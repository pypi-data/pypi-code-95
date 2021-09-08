import datetime

from SapphireQuant.Config.TradingDay import HolidayHelper
from SapphireQuant.Config.TradingDay.TradingDayHelper import TradingDayHelper
from SapphireQuant.Core.DateTimeSlice import DateTimeSlice
from SapphireQuant.Core.Enum import EnumMarket
from SapphireQuant.Core.Enum.EnumBarType import EnumBarType
from SapphireQuant.Core.TimeSlice import TimeSlice
from SapphireQuant.DataProcessing.BarProviderInfo import BarProviderInfo
from SapphireQuant.Core.YfTimeHelper import YfTimeHelper
import pandas as pd


class BaseBarHelper:
    """
    基础K线帮助类
    """
    one_day = datetime.timedelta(days=1)

    def __init__(self):
        self.__templates = []

    @staticmethod
    def create_bar_provider_info(lst_time_slice, offset, interval, bar_type):
        """

        :param lst_time_slice:
        :param offset:
        :param interval:
        :param bar_type:
        :return:
        """
        bars = BaseBarHelper.create_time_slices(lst_time_slice, offset, interval, bar_type)
        if bars is None:
            return None

        bar_provider_info = BarProviderInfo()
        bar_provider_info.time_slices = bars
        bar_provider_info.bar_type = bar_type
        bar_provider_info.interval = interval
        bar_provider_info.offset = offset
        bar_provider_info.living_time = TimeSlice()
        bar_provider_info.living_time.begin_time = lst_time_slice[0].begin_time
        bar_provider_info.living_time.end_time = lst_time_slice[-1].end_time

    @staticmethod
    def create_time_slice(lst_time_slice, offset, interval, bar_type):
        """
        切分时间片段
        根据一天的交易时间片段，按照给定的K线参数，进行时间片段的划分
        :param lst_time_slice:源生时间片段
        :param offset:位移
        :param interval:间隔
        :param bar_type:K线类型
        :return:
        """
        if len(lst_time_slice) == 0:
            return None

        offset_time_span = datetime.timedelta(0, 0, offset)
        if bar_type == EnumBarType.second:
            interval_time_span = datetime.timedelta(seconds=interval)
        elif bar_type == EnumBarType.minute:
            interval_time_span = datetime.timedelta(minutes=interval)
        elif bar_type == EnumBarType.hour:
            interval_time_span = datetime.timedelta(hours=interval)
        elif bar_type == EnumBarType.day:
            day_time_slice = TimeSlice()
            day_time_slice.begin_time = lst_time_slice[0].begin_time
            day_time_slice.end_time = lst_time_slice[-1].end_time
            day_bars = [day_time_slice]
            return day_bars
        else:
            raise Exception("不支持的K线:" + str(bar_type))

        begin_time = lst_time_slice[0].begin_time
        bars = []
        if offset > 0:
            slice = TimeSlice()
            slice.begin_time = begin_time
            slice.end_time = begin_time + offset_time_span
            if slice.end_time.days() > 0:
                slice.end_time = slice.end_time = BaseBarHelper.one_day

            bars.append(slice)

            begin_time = slice.end_time

        end_time = begin_time
        diff_time_span = datetime.timedelta(0, 0, 0)
        for i in range(len(lst_time_slice)):
            ts = lst_time_slice[i]
            while True:
                tmp = ts.end_time - end_time
                if tmp < datetime.timedelta(0, 0, 0):
                    tmp = tmp + BaseBarHelper.one_day

                if (tmp + diff_time_span) < interval_time_span:
                    break

                end_time = end_time + (interval_time_span - diff_time_span)
                if end_time >= BaseBarHelper.one_day:
                    end_time = end_time - BaseBarHelper.one_day

                slice = TimeSlice()
                slice.begin_time = begin_time
                slice.end_time = end_time
                bars.append(slice)

                begin_time = end_time
                diff_time_span = datetime.timedelta(0, 0, 0)

            if i < (len(lst_time_slice) - 1):
                diff_time_span = diff_time_span + ts.end_time - end_time
                if diff_time_span < datetime.timedelta(0, 0, 0):
                    diff_time_span = diff_time_span + BaseBarHelper.one_day

                end_time = lst_time_slice[i + 1].begin_time

                if diff_time_span == datetime.timedelta(0, 0, 0):
                    begin_time = end_time
            else:
                if begin_time < ts.end_time:
                    slice = TimeSlice()
                    slice.begin_time = begin_time
                    slice.end_time = ts.end_time
                    bars.append(slice)

        return bars

    @staticmethod
    def create_date_time_slice(trading_day, lst_time_slices):
        """
        根据时间片段生成交日期时间片段
        :param trading_day:交易日
        :param lst_time_slices:时间片段
        :return:
        """
        pre_trading_day1 = TradingDayHelper.get_pre_trading_day(trading_day)
        pre_trading_day2 = pre_trading_day1 + datetime.timedelta(days=1)

        lst_date_time_slice = []
        for timeSlice in lst_time_slices:
            date_time_slice = DateTimeSlice()
            date_time_slice.begin_time = YfTimeHelper.join_date_time(trading_day, pre_trading_day1, pre_trading_day2, timeSlice.begin_time)
            date_time_slice.end_time = YfTimeHelper.join_date_time(trading_day, pre_trading_day1, pre_trading_day2, timeSlice.end_time)
            lst_date_time_slice.append(date_time_slice)
        return lst_date_time_slice

    @staticmethod
    def create_out_day_date_time_slice_by_date(begin_date, end_date, interval, bar_type):
        """
        非日内时间片段：据日期区间创建日内的日期时间片段
        :param begin_date:开始时间
        :param end_date:结束时间
        :param interval:间隔
        :param bar_type:K线类型
        :return:
        """
        lst_date_time_slice = []
        begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_trading_day = TradingDayHelper.get_last_trading_day(end_date)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        end_index = len(lst_trading_days) - 1
        start_index = end_index - interval + 1
        while (end_index >= 0) & (start_index >= 0):
            begin_date = lst_trading_days[start_index]
            end_date = lst_trading_days[end_index]

            date_time_slice = DateTimeSlice()
            date_time_slice.begin_time = begin_date
            date_time_slice.end_time = end_date
            lst_date_time_slice.insert(0, date_time_slice)

            end_index = end_index - interval
            start_index = end_index - interval + 1

        if end_index >= 0:
            begin_date = lst_trading_days[0]
            end_date = lst_trading_days[end_index]

            date_time_slice = DateTimeSlice()
            date_time_slice.begin_time = begin_date
            date_time_slice.end_time = end_date
            lst_date_time_slice.insert(0, date_time_slice)

        return lst_date_time_slice

    @staticmethod
    def create_out_day_date_time_slice_by_date_time(begin_time, end_time, interval, bar_type):
        """
        非日内时间片段：据时间区间创建日内的日期时间片段
        :param begin_time:开始时间
        :param end_time:结束时间
        :param interval:间隔
        :param bar_type:K线类型
        :return:
        """
        begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
        end_trading_day = YfTimeHelper.get_trading_day(end_time)
        return BaseBarHelper.create_out_day_date_time_slice_by_date(begin_trading_date, end_trading_day, interval, bar_type)

    @staticmethod
    def create_in_day_date_time_slice_by_date_time(instrument_manager, instrument_id, begin_time, end_time, interval, bar_type, *instrument_ids):
        """
        日内时间片段：根据时间区间创建日内的日期时间片段
        片段开始结束精确到时分秒
        :param instrument_manager:合约管理器
        :param instrument_id:合约编号
        :param begin_time:开始时间
        :param end_time:截止时间
        :param interval:间隔
        :param bar_type:K线类型
        :param instrument_ids:参与交易时间交集的交易品种列表
        :return:
        """
        lst_all_date_time_slices = []
        begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
        end_trading_day = YfTimeHelper.get_trading_day(end_time)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        for trading_day in lst_trading_days:
            lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
            lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
            lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
            for dateTimeSlice in lst_date_time_slices:
                if (dateTimeSlice.end_time >= begin_time) & (dateTimeSlice.end_time <= end_time):
                    lst_all_date_time_slices.append(dateTimeSlice)

        return lst_all_date_time_slices

    @staticmethod
    def create_in_day_date_time_slice_by_date(instrument_manager, instrument_id, begin_date, end_date, interval, bar_type, *instrument_ids):
        """
        根据日期区间创建日内的日期时间片段
        :param instrument_manager:合约管理器
        :param instrument_id:合约编号
        :param begin_date:开始时间
        :param end_date:截止时间
        :param interval:间隔
        :param bar_type:K线类型
        :param instrument_ids:参与交易时间交集的交易品种列表
        :return:
        """
        lst_all_date_time_slices = []
        begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_trading_day = TradingDayHelper.get_last_trading_day(end_date)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        for trading_day in lst_trading_days:
            lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
            lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
            lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
            for dateTimeSlice in lst_date_time_slices:
                lst_all_date_time_slices.append(dateTimeSlice)

        return lst_all_date_time_slices

    @staticmethod
    def create_in_day_date_time_slice_by_date_24h(begin_date, end_date, interval, bar_type):
        """
        根据日期区间创建日内的日期时间片段 24小时交易的
        :param begin_date:开始时间
        :param end_date:截止时间
        :param interval:间隔
        :param bar_type:K线类型
        :return:
        """
        lst_all_date_time_slices = []
        trading_day = begin_date
        delta = datetime.timedelta(days=1)
        while trading_day <= end_date:
            time_slice = TimeSlice(begin_time=datetime.timedelta(hours=0, minutes=0, seconds=0), end_time=datetime.timedelta(hours=23, minutes=59, seconds=0))
            lst_trading_time_slices = [time_slice]
            lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
            for time_slices in lst_time_slices:
                date_time_slices = DateTimeSlice()
                date_time_slices.begin_time = trading_day + time_slices.begin_time
                date_time_slices.end_time = trading_day + time_slices.end_time
                lst_all_date_time_slices.append(date_time_slices)

            trading_day += delta
        return lst_all_date_time_slices

    @staticmethod
    def create_in_day_date_time_slice_by_date_consider_holiday(instrument_manager, instrument_id, begin_date, end_date, interval, bar_type, *instrument_ids):
        """
        根据日期区间创建日内的日期时间片段
        :param instrument_manager:合约管理器
        :param instrument_id:合约编号
        :param begin_date:开始时间
        :param end_date:截止时间
        :param interval:间隔
        :param bar_type:K线类型
        :param instrument_ids:参与交易时间交集的交易品种列表
        :return:
        """
        lst_all_date_time_slices = []
        begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_trading_day = TradingDayHelper.get_last_trading_day(end_date)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        listing_date = instrument_manager.get_listing_date(EnumMarket.期货, instrument_id)
        for trading_day in lst_trading_days:
            lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
            lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
            lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
            for dateTimeSlice in lst_date_time_slices:
                if trading_day == listing_date or HolidayHelper.is_post_holiday_trading_date(trading_day):
                    if dateTimeSlice.begin_time.hour > 6 and (dateTimeSlice.begin_time.hour < 18):  # 只有日盘
                        lst_all_date_time_slices.append(dateTimeSlice)
                else:
                    lst_all_date_time_slices.append(dateTimeSlice)

        return lst_all_date_time_slices

    @staticmethod
    def create_data_frame_in_day_date_time_slice_by_date_consider_holiday(instrument_manager, instrument_id, begin_date, end_date, interval, bar_type, *instrument_ids):
        """
        根据日期区间创建日内的日期时间片段的DataFrame
        :param instrument_manager:合约管理器
        :param instrument_id:合约编号
        :param begin_date:开始时间
        :param end_date:截止时间
        :param interval:间隔
        :param bar_type:K线类型
        :param instrument_ids:参与交易时间交集的交易品种列表
        :return:
        """
        lst_all_date_time_slices = []
        begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_trading_day = TradingDayHelper.get_last_trading_day(end_date)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        listing_date = instrument_manager.get_listing_date(EnumMarket.期货, instrument_id)
        for trading_day in lst_trading_days:
            lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
            lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
            lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
            for dateTimeSlice in lst_date_time_slices:
                if trading_day == listing_date or HolidayHelper.is_post_holiday_trading_date(trading_day):
                    if dateTimeSlice.begin_time.hour > 6 and (dateTimeSlice.begin_time.hour < 18):  # 只有日盘
                        lst_all_date_time_slices.append([dateTimeSlice.begin_time, dateTimeSlice.end_time])
                else:
                    lst_all_date_time_slices.append([dateTimeSlice.begin_time, dateTimeSlice.end_time])

        df_all_date_time_slices = pd.DataFrame(lst_all_date_time_slices, columns=['begin_time', 'end_time'])
        return df_all_date_time_slices

    @staticmethod
    def create_night_am_pm_date_time_slice_by_date(instrument_manager, instrument_id, begin_date, end_date, *instrument_ids):
        """
        根据日期区间创建日内的日期时间片段
        :param instrument_manager:合约管理器
        :param instrument_id:合约编号
        :param begin_date:开始时间
        :param end_date:截止时间
        :param instrument_ids:参与交易时间交集的交易品种列表
        :return:
        """
        lst_all_date_time_slices = []
        begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_trading_day = TradingDayHelper.get_last_trading_day(end_date)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_day)
        for trading_day in lst_trading_days:
            lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
            lst_time_slices = []
            for i in range(len(lst_trading_time_slices)):
                if 10 <= (lst_trading_time_slices[i].begin_time.seconds / (60 * 60)) <= 11:
                    lst_time_slices[i - 1].end_time = lst_trading_time_slices[i].end_time
                else:
                    lst_time_slices.append(lst_trading_time_slices[i])
            lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
            for dateTimeSlice in lst_date_time_slices:
                lst_all_date_time_slices.append(dateTimeSlice)

        return lst_all_date_time_slices

    @staticmethod
    def create_one_day_date_time_slice(instrument_manager, instrument_id, trading_day, interval, bar_type, *instrument_ids):
        """
        创建一天的日期时间片段
        :param instrument_manager:合约管理器
        :param instrument_id:合约编号
        :param trading_day:交易日
        :param interval:间隔
        :param bar_type:K线类型
        :param instrument_ids:参与交易时间交集的交易品种列表
        :return:
        """
        lst_trading_time_slices = instrument_manager.get_trading_time(trading_day, instrument_id, *instrument_ids)
        lst_time_slices = BaseBarHelper.create_time_slice(lst_trading_time_slices, 0, interval, bar_type)
        lst_date_time_slices = BaseBarHelper.create_date_time_slice(trading_day, lst_time_slices)
        return lst_date_time_slices
