import datetime
import math
import os
import sys

from dateutil.relativedelta import relativedelta

from SapphireQuant.Config.Instrument.InstrumentManager import InstrumentManager
from SapphireQuant.Config.TradingDay.TradingDayHelper import TradingDayHelper
from SapphireQuant.Core.Bar import Bar
from SapphireQuant.Core.Enum.EnumBarType import EnumBarType
from SapphireQuant.Core.Enum.EnumMarket import EnumMarket
from SapphireQuant.Core.Enum.EnumRestoration import EnumRestoration
from SapphireQuant.Core.TickSeries import TickSeries
from SapphireQuant.DataProcessing.BarProvider import BarProvider
from SapphireQuant.DataProcessing.BaseBarHelper import BaseBarHelper
from SapphireQuant.DataProcessing.BinaryDayBarStream import BinaryDayBarStream
from SapphireQuant.DataProcessing.BinaryDcTickStream import BinaryDcTickStream
from SapphireQuant.DataProcessing.BinaryMinBarStream import BinaryMinBarStream
from SapphireQuant.DataProcessing.BinaryTickStream import BinaryTickStream
from SapphireQuant.Core.YfTimeHelper import YfTimeHelper
import pandas as pd


class QiDataController:
    """
    量化投资数据句柄
    """

    def __init__(self, qi_data_directory):
        config_dir = os.path.join(sys.modules["ROOT_DIR"], 'Profiles')
        instrument_manager = InstrumentManager()
        instrument_manager.load(config_dir, EnumMarket.期货)

        self.data_directory = qi_data_directory
        self.instrument_manager = instrument_manager
        self.trading_day = qi_data_directory.trading_day

        self.__future_tick_path = qi_data_directory.future_tick
        self.__future_tick_cache_path = qi_data_directory.future_tick_cache
        self.__future_min_path = qi_data_directory.future_min
        self.__future_day_path = qi_data_directory.future_day

        self.__bar_series_map = {}
        self.__tick_series_map = {}

    def init(self, trading_date):
        """
        重新初始化句柄交易日和缓存数据
        :param trading_date:
        """
        self.trading_day = trading_date
        self.__bar_series_map.clear()
        self.__tick_series_map.clear()

    def __load_today_tick_series(self, market, instrument_id, trading_date):
        path = self.__future_tick_cache_path
        tick_series = TickSeries()
        try:
            file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
            file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
            if market == EnumMarket.期货:
                if instrument_id.lower() != 'index':
                    instrument = self.instrument_manager[instrument_id.split('.')[0]]
                    tick_stream = BinaryTickStream(market, instrument_id, instrument.exchange_id, file_path)
                    tick_stream.read_by_count(tick_series, 0, sys.maxsize)
            elif market == EnumMarket.数字货币:
                exchange_id = 'HUOBI'
                tick_stream = BinaryDcTickStream(market, instrument_id, exchange_id, file_path)
                tick_stream.read_by_count(tick_series, 0, sys.maxsize)
        except Exception as e:
            print(str(e))

        return tick_series

    def __load_history_tick_series(self, market, instrument_id, trading_date):
        path = self.__future_tick_path
        tick_series = TickSeries()
        try:
            if market == EnumMarket.期货:
                file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
                if instrument_id.lower() != 'index':
                    instrument = self.instrument_manager[instrument_id.split('.')[0]]
                    tick_stream = BinaryTickStream(market, instrument_id, instrument.exchange_id, file_path)
                    tick_stream.read_by_count(tick_series, 0, sys.maxsize)
            elif market == EnumMarket.数字货币:
                file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
                if instrument_id.lower() != 'index':
                    exchange_id = 'HUOBI'
                    tick_stream = BinaryDcTickStream(market, instrument_id, exchange_id, file_path)
                    tick_stream.read_by_count(tick_series, 0, sys.maxsize)
        except Exception as e:
            print(str(e))

        return tick_series

    def load_min_bar_series(self, market, instrument_id, *trading_dates):
        """
        根据交易日信息加载历史分钟线数据
        :param market:
        :param instrument_id:
        :param trading_dates:
        :return:
        """
        path = self.__future_min_path
        bar_series = []
        try:
            if len(trading_dates) == 1:
                trading_date = trading_dates[0]
                trading_date = datetime.datetime(trading_date.year, trading_date.month, trading_date.day)

                file_path = os.path.join(path, trading_date.strftime('%Y%m'))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".min")
                if instrument_id.lower() != 'index':
                    min_bar_steam = BinaryMinBarStream(market, instrument_id, file_path)
                    min_bar_steam.read_trading_day(bar_series, trading_date)

            if len(trading_dates) == 2:
                begin_date = trading_dates[0]
                end_date = trading_dates[1]
                begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
                end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)

                begin_month = datetime.datetime(begin_date.year, begin_date.month, 1)
                end_month = datetime.datetime(end_date.year, end_date.month, 1) + relativedelta(months=+1) + datetime.timedelta(days=-1)
                date = begin_month
                while date <= end_month:
                    file_path = os.path.join(path, date.strftime('%Y%m'))
                    file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".min")
                    min_bar_steam = BinaryMinBarStream(market, instrument_id, file_path)
                    min_bar_steam.read_trading_days(bar_series, begin_date, end_date)
                    date = date + relativedelta(months=+1)
        except Exception as e:
            print(str(e))

        return bar_series

    def load_day_bar_series(self, market, instrument_id, *trading_dates):
        """
        根据交易日信息加载历史日线数据
        :param market:市场
        :param instrument_id:合约编号
        :param trading_dates:
        :return:K线
        """
        path = self.__future_day_path
        bar_series = []
        begin_date = trading_dates[0]
        try:
            if len(trading_dates) == 1:
                trading_date = trading_dates[0]
                trading_date = datetime.datetime(trading_date.year, trading_date.month, trading_date.day)

                # 这边做了修改，由于数据问题，不得不多加载一天的历史数据，来修复日线bar.pre_close的错误问题
                pre_begin_date = TradingDayHelper.get_pre_trading_day(trading_date)
                begin_month = datetime.datetime(pre_begin_date.year, pre_begin_date.month, 1)
                end_month = datetime.datetime(trading_date.year, trading_date.month, 1) + relativedelta(months=+1) + datetime.timedelta(days=-1)
                date = begin_month
                while date <= end_month:
                    file_path = os.path.join(path, date.strftime('%Y%m'))
                    file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".day")
                    day_bar_steam = BinaryDayBarStream(market, instrument_id, file_path)
                    day_bar_steam.read(bar_series, pre_begin_date, trading_date)
                    date = date + relativedelta(months=+1)

            if len(trading_dates) == 2:
                begin_date = trading_dates[0]
                end_date = trading_dates[1]
                begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
                end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)

                # 这边做了修改，由于数据问题，不得不多加载一天的历史数据，来修复日线bar.pre_close的错误问题
                pre_begin_date = TradingDayHelper.get_pre_trading_day(begin_date)
                begin_month = datetime.datetime(pre_begin_date.year, pre_begin_date.month, 1)
                end_month = datetime.datetime(end_date.year, end_date.month, 1) + relativedelta(months=+1) + datetime.timedelta(days=-1)
                date = begin_month
                while date <= end_month:
                    file_path = os.path.join(path, date.strftime('%Y%m'))
                    file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".day")
                    day_bar_steam = BinaryDayBarStream(market, instrument_id, file_path)
                    day_bar_steam.read(bar_series, pre_begin_date, end_date)
                    date = date + relativedelta(months=+1)
        except Exception as e:
            print(str(e))

        # 新增的数据处理来修复日线bar.pre_close的错误问题
        bar_series_processed = []
        pre_bar = None
        for bar in bar_series:
            if pre_bar is not None:
                bar.pre_close = pre_bar.close
            pre_bar = bar
            if bar.begin_time >= begin_date:
                bar_series_processed.append(bar)
        return bar_series_processed

    def load_tick_series(self, market, instrument_id, *trading_dates):
        """
        根据交易日信息加载历史Tick数据
        :param market:市场
        :param instrument_id:合约编号
        :param trading_dates:交易日
        :return:
        """
        if len(trading_dates) == 1:
            trading_date = trading_dates[0]
            trading_date = datetime.datetime(trading_date.year, trading_date.month, trading_date.day)
            return self.__load_history_tick_series(market, instrument_id, trading_date)
        else:
            begin_date = trading_dates[0]
            end_date = trading_dates[1]
            begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
            end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)

            all_ticks = []
            try:
                begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
                end_trading_date = TradingDayHelper.get_last_trading_day(end_date)
                date = begin_trading_date
                while date <= end_trading_date:
                    temp_ticks = self.__load_history_tick_series(market, instrument_id, date)
                    all_ticks.extend(temp_ticks)
                    date = TradingDayHelper.get_next_trading_day(date)
            except Exception as e:
                print(str(e))

            return all_ticks

    def load_tick_series_by_date_time(self, market, instrument_id, begin_time, end_time):
        """
        根据时间区间加载历史Tick数据
        :param market:市场
        :param instrument_id:合约编号
        :param begin_time:开始时间
        :param end_time:截止时间
        :return:
        """
        path = self.__future_tick_path
        all_ticks = []
        try:
            begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
            end_trading_date = YfTimeHelper.get_trading_day(end_time)
            date = begin_trading_date
            while date <= end_trading_date:
                file_path = os.path.join(path, date.strftime("%Y%m%d"))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
                if instrument_id.lower() != "index":
                    instrument = self.instrument_manager[instrument_id.split('.')[0]]
                    tick_stream = BinaryTickStream(market, instrument_id, instrument.exchange_id, file_path)
                    tick_stream.read_by_time(all_ticks, begin_time, end_time)

                date = date + datetime.timedelta(days=1)
        except Exception as e:
            print(str(e))

        return all_ticks

    def load_tick_series_real(self, market, instrument_id, begin_time, end_time):
        """
        实盘根据时间区间获取Tick数据
        会根据DataHandler设置的交易日判断，将begin_time-end_time的区间切分成历史区间和当日区间
        历史区间：begin_time-昨日收盘
        当日区间:当日开盘-end_time
        若需要加载历史交易日Tick，则从历史目录加载数据
        若需要加载当日交易日Tick，则从当日目录加载数据
        :param market:市场
        :param instrument_id:合约编号
        :param begin_time:开始时间
        :param end_time:截止时间
        :return:
        """
        path = self.__future_tick_path
        all_ticks = []
        try:
            begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
            last_trading_day = YfTimeHelper.get_trading_day(end_time)
            if last_trading_day == self.trading_day:
                end_trading_date = TradingDayHelper.get_pre_trading_day(last_trading_day)
            else:
                end_trading_date = last_trading_day
            date = begin_trading_date
            while date <= end_trading_date:
                file_path = os.path.join(path, date.strftime("%Y%m%d"))
                file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
                if instrument_id.lower() != "index":
                    instrument = self.instrument_manager[instrument_id.split('.')[0]]
                    tick_stream = BinaryTickStream(market, instrument_id, instrument.exchange_id, file_path)
                    tick_stream.read_by_time(all_ticks, begin_time, end_time)

                date = date + datetime.timedelta(days=1)

            if end_trading_date != last_trading_day:
                tick_series = self.__load_today_tick_series(market, instrument_id, self.trading_day)
                all_ticks.extend(tick_series)
        except Exception as e:
            print(str(e))

        return all_ticks

    def load_bar_series_by_date(self, market, instrument_id, interval, bar_type, begin_date, end_date, *instrument_ids):
        """
        根据日期区间加载历史K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param begin_date:
        :param end_date:
        :param instrument_ids:
        :return:
        """
        if market == EnumMarket.期货:
            begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
            end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
            begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
            end_trading_date = TradingDayHelper.get_last_trading_day(end_date)
            lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval,
                                                     bar_type, *instrument_ids)
            if bar_type == EnumBarType.second:
                for trading_day in lst_trading_days:
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
            elif (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
                bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
                for bar in bar_series_min:
                    bar_provider.add_bar(bar)
            elif bar_type == EnumBarType.day:
                bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
                for bar in bar_series_day:
                    bar_provider.add_bar(bar)
            else:
                raise Exception("不支持的k线:" + str(bar_type))

            return bar_provider.bar_series
        elif market == EnumMarket.数字货币:
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date_24h(begin_date, end_date, interval, bar_type)
            if bar_type == EnumBarType.second:
                trading_day = begin_date
                while trading_day <= end_date:
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
                    trading_day = trading_day + datetime.timedelta(days=1)
            elif (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
                bar_series_min = self.load_min_bar_series(market, instrument_id, begin_date, end_date)
                for bar in bar_series_min:
                    bar_provider.add_bar(bar)
            elif bar_type == EnumBarType.day:
                bar_series_day = self.load_day_bar_series(market, instrument_id, begin_date, end_date)
                for bar in bar_series_day:
                    bar_provider.add_bar(bar)
            else:
                raise Exception("不支持的k线:" + str(bar_type))

            return bar_provider.bar_series

    def load_bar_series_by_date_time(self, market, instrument_id, interval, bar_type, begin_time, end_time, *instrument_ids):
        """
        根据时间区间加载历史K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param begin_time:
        :param end_time:
        :param instrument_ids:
        :return:
        """
        if market == EnumMarket.期货:
            begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
            end_trading_date = YfTimeHelper.get_trading_day(end_time)
            lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date_time(self.instrument_manager, instrument_id, begin_time, end_time, interval, bar_type,
                                                          *instrument_ids)
            if bar_type == EnumBarType.second:
                for trading_day in lst_trading_days:
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
            elif (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
                bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
                for bar in bar_series_min:
                    bar_provider.add_bar(bar)
            elif bar_type == EnumBarType.day:
                bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
                for bar in bar_series_day:
                    bar_provider.add_bar(bar)
            else:
                raise Exception("不支持的k线:" + str(bar_type))

            return bar_provider.bar_series
        else:
            raise Exception("不支持的市场:" + str(market))

    def load_bar_series_by_length(self, market, instrument_id, interval, bar_type, max_length, end_date, *instrument_ids):
        """
        根据结束日期加载指定回溯根数的历史K线（K线数据包含结束日期）
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param max_length:
        :param end_date:
        :param instrument_ids:
        :return:
        """
        # 这里为了提升取数据的速度,根据时间预计算根数,不足再补
        if market == EnumMarket.期货:
            end_trading_date = TradingDayHelper.get_last_trading_day(end_date)
            lst_date_time_slices_one_day = BaseBarHelper.create_one_day_date_time_slice(
                self.instrument_manager, instrument_id, end_trading_date, interval, bar_type, *instrument_ids)
            if len(lst_date_time_slices_one_day) > 0:
                n_one_day_count = len(lst_date_time_slices_one_day)
            else:
                n_one_day_count = 1

            n_trading_days = int(math.ceil(max_length * 1.0 / n_one_day_count))
            if bar_type == EnumBarType.day:
                n_trading_days = n_trading_days * interval
            else:
                n_trading_days = n_trading_days

            begin_trading_date = TradingDayHelper.get_pre_trading_day(end_trading_date, n_trading_days - 1)
            lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date(
                self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval, bar_type, *instrument_ids)
            if bar_provider.bar_type == EnumBarType.second:
                for trading_day in lst_trading_days:
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
            elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
                for bar in bar_series_min:
                    bar_provider.add_bar(bar)
            elif bar_provider.bar_type == EnumBarType.day:
                bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
                for bar in bar_series_day:
                    bar_provider.add_bar(bar)
            else:
                raise Exception("不支持的k线:" + str(bar_type))

            bar_series = bar_provider.bar_series
            if len(bar_provider.bar_series) < max_length:
                trading_date = begin_trading_date
                count = 0
                while count < 5:
                    count += 1
                    trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
                    if bar_provider.bar_type == EnumBarType.second:
                        bar_provider = BarProvider()
                        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                        tick_series = self.__load_history_tick_series(market, instrument_id, trading_date)
                        for tick in tick_series:
                            bar_provider.add_tick(tick)
                    elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                        bar_provider = BarProvider()
                        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                        bar_series_min = self.load_min_bar_series(market, instrument_id, trading_date)
                        for bar in bar_series_min:
                            bar_provider.add_bar(bar)
                    elif bar_provider.bar_type == EnumBarType.day:
                        begin_date = TradingDayHelper.get_pre_trading_day(trading_date, interval - 1)
                        bar_provider = BarProvider()
                        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                        bar_series_day = self.load_day_bar_series(market, instrument_id, begin_date, end_trading_date)
                        trading_date = begin_date
                        for bar in bar_series_day:
                            bar_provider.add_bar(bar)
                    else:
                        raise Exception("不支持的k线:" + str(bar_type))

                    bar_provider.bar_series.extend(bar_series)
                    bar_series = bar_provider.bar_series

                    if len(bar_series) >= max_length:
                        break

            bar_provider = BarProvider()
            next_trading_date = TradingDayHelper.get_next_trading_day(end_trading_date)
            bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, next_trading_date, interval, bar_type, *instrument_ids)
            for bar in bar_series:
                bar_provider.bar_series.append(bar)

            remove_length = len(bar_provider.bar_series) - max_length
            if remove_length > 0:
                del bar_provider.bar_series[0:remove_length]

            return bar_provider.bar_series
        else:
            raise Exception("不支持的市场:" + str(market))

    def load_night_am_pm_bar_series_by_date(self, market, instrument_id, begin_date, end_date, *instrument_ids):
        """
        根据日期区间加载历史K线
        :param market:
        :param instrument_id:
        :param begin_date:
        :param end_date:
        :param instrument_ids:
        :return:
        """
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        begin_trading_date = TradingDayHelper.get_first_trading_day(begin_date)
        end_trading_date = TradingDayHelper.get_last_trading_day(end_date)
        bar_provider = BarProvider()
        bar_provider.create_night_am_pm_bar_provider_by_date(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, *instrument_ids)
        bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
        for bar in bar_series_min:
            bar_provider.add_bar(bar)

        return bar_provider.bar_series

    def load_night_am_pm_bar_series_by_length(self, market, instrument_id, max_length, end_date, *instrument_ids):
        """
        根据结束日期加载指定回溯根数的历史K线（K线数据包含结束日期）
        :param market:
        :param instrument_id:
        :param max_length:
        :param end_date:
        :param instrument_ids:
        :return:
        """
        # 这里为了提升取数据的速度,根据时间预计算根数,不足再补
        end_trading_date = TradingDayHelper.get_last_trading_day(end_date)
        n_one_day_count = 2  # 默认等2 这样可以预载多一点的K线，再做切除

        n_trading_days = int(math.ceil(max_length * 1.0 / n_one_day_count))

        begin_trading_date = TradingDayHelper.get_pre_trading_day(end_trading_date, n_trading_days - 1)
        bar_provider = BarProvider()
        bar_provider.create_night_am_pm_bar_provider_by_date(
            self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, *instrument_ids)
        bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
        for bar in bar_series_min:
            bar_provider.add_bar(bar)

        bar_series = bar_provider.bar_series
        if len(bar_provider.bar_series) < max_length:
            trading_date = begin_trading_date
            count = 0
            while count < 5:
                count += 1
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
                bar_provider = BarProvider()
                bar_provider.create_night_am_pm_bar_provider_by_date(self.instrument_manager, instrument_id, trading_date, trading_date, *instrument_ids)
                bar_series_min = self.load_min_bar_series(market, instrument_id, trading_date)
                for bar in bar_series_min:
                    bar_provider.add_bar(bar)

                bar_provider.bar_series.extend(bar_series)
                bar_series = bar_provider.bar_series

                if len(bar_series) >= max_length:
                    break

        bar_provider = BarProvider()
        next_trading_date = TradingDayHelper.get_next_trading_day(end_trading_date)
        bar_provider.create_night_am_pm_bar_provider_by_date(self.instrument_manager, instrument_id, next_trading_date, next_trading_date, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        remove_length = len(bar_provider.bar_series) - max_length
        if remove_length > 0:
            del bar_provider.bar_series[0:remove_length]

        return bar_provider.bar_series

    def load_bar_series_by_length_limit_end_time(self, market, instrument_id, interval, bar_type, max_length, end_time, *instrument_ids):
        """
        根据结束时间加载指定回溯根数的历史K线（K线数据都小于等于结束时间）
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param max_length:
        :param end_time:
        :param instrument_ids:
        :return:
        """
        # 这里为了提升取数据的速度,根据时间预计算根数,不足再补
        end_trading_date = YfTimeHelper.get_trading_day(end_time)
        end_trading_date = TradingDayHelper.get_last_trading_day(end_trading_date)
        lst_date_time_slices_one_day = BaseBarHelper.create_one_day_date_time_slice(
            self.instrument_manager, instrument_id, end_trading_date, interval, bar_type, *instrument_ids)
        if len(lst_date_time_slices_one_day) > 0:
            n_one_day_count = len(lst_date_time_slices_one_day)
        else:
            n_one_day_count = 1

        n_trading_days = int(math.ceil(max_length * 1.0 / n_one_day_count))
        if bar_type == EnumBarType.day:
            n_trading_days = n_trading_days * interval
        else:
            n_trading_days = n_trading_days

        begin_trading_date = TradingDayHelper.get_pre_trading_day(end_trading_date, n_trading_days - 1)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        bar_provider = BarProvider()
        trading_time = self.instrument_manager.get_trading_time(begin_trading_date, instrument_id)
        begin_time = TradingDayHelper.get_natural_date_time(begin_trading_date, trading_time[0].begin_time)
        bar_provider.create_bar_provider_by_date_time(self.instrument_manager, instrument_id, begin_time, end_time, interval, bar_type,
                                                      *instrument_ids)
        if bar_provider.bar_type == EnumBarType.second:
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_provider.bar_type == EnumBarType.day:
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        bar_series = bar_provider.bar_series
        if len(bar_provider.bar_series) < max_length:
            trading_date = begin_trading_date
            count = 0
            while count < 5:
                count += 1
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
                if bar_provider.bar_type == EnumBarType.second:
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_date)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
                elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_min = self.load_min_bar_series(market, instrument_id, trading_date)
                    for bar in bar_series_min:
                        bar_provider.add_bar(bar)
                elif bar_provider.bar_type == EnumBarType.day:
                    begin_date = TradingDayHelper.get_pre_trading_day(trading_date, interval - 1)
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_day = self.load_day_bar_series(market, instrument_id, begin_date, end_trading_date)
                    trading_date = begin_date
                    for bar in bar_series_day:
                        bar_provider.add_bar(bar)
                else:
                    raise Exception("不支持的k线:" + str(bar_type))

                bar_provider.bar_series.extend(bar_series)
                bar_series = bar_provider.bar_series

                if len(bar_series) >= max_length:
                    break

        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, self.trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        remove_length = len(bar_provider.bar_series) - max_length
        if remove_length > 0:
            del bar_provider.bar_series[0:remove_length]

        return bar_provider.bar_series

    def get_tick_series_by_time(self, market, instrument_id, begin_time, end_time):
        """
        实盘根据时间区间获取Tick数据
        注意：若之前已经获取过品种的Tick数据，则直接从缓存返回Tick数据，不会根据变化的begin_time和end_time从新加载Tick数据
        :param market:市场
        :param instrument_id:合约编号
        :param begin_time:开始时间
        :param end_time:截止时间
        :return:
        """
        if instrument_id not in self.__tick_series_map.keys():
            all_ticks = self.load_tick_series_real(market, instrument_id, begin_time, end_time)
            self.__tick_series_map[instrument_id] = all_ticks
        else:
            all_ticks = self.__tick_series_map[instrument_id]
        return all_ticks

    def get_tick_series_by_length(self, market, instrument_id, end_time, length):
        """
        实盘根据时间区间获取Tick数据
        注意：
        若之前已经获取过品种的Tick数据，则直接从缓存返回Tick数据，
        若之前没有获取过品种的Tick数据，则加载Tick数据到缓存，并返回
        :param market:市场
        :param instrument_id:合约编号
        :param end_time:截止时间
        :param length:长度
        :return:
        """
        tick_series = []
        if instrument_id not in self.__tick_series_map.keys():
            lst_ticks = []
            end_trading_date = YfTimeHelper.get_trading_day(end_time)
            trading_date = TradingDayHelper.get_last_trading_day(end_trading_date)
            while len(lst_ticks) < length:
                temp_lst_ticks = lst_ticks.copy()
                temp_tick_series = self.load_tick_series(market, instrument_id, trading_date)
                lst_ticks.clear()
                for tick in temp_tick_series:
                    if tick.end_time <= end_time:
                        lst_ticks.append(tick)
                lst_ticks.extend(temp_lst_ticks)
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
            tick_series = lst_ticks[-length:]
            self.__tick_series_map[instrument_id] = tick_series
        else:
            tick_series = self.__tick_series_map[instrument_id]
        return tick_series

    def get_bar_series_by_time(self, market, instrument_id, interval, bar_type, begin_time, end_time, restore=EnumRestoration.不复权, *instrument_ids):
        """
        实盘根据时间区间获取K线
        历史K线从历史数据直接加载组装
        当日K线根据Tick数据组装
        最后合并历史和当日K线，并返回
        注意：
        若之前已经获取过品种的K线数据，则直接从缓存返回K线，(判断条件：interval，bar_type的唯一性)
        若之前没有获取过品种的K线数据，则加载K线数据到缓存，并返回
        :param market:市场
        :param instrument_id:合约编号
        :param interval:间隔
        :param bar_type:K线类型
        :param begin_time:开始时间
        :param end_time:截止时间
        :param restore:复权方式
        :param instrument_ids:参与求交易时间交集的品种
        :return:
        """
        bar_providers = []
        if instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[instrument_id]
        else:
            self.__bar_series_map[instrument_id] = bar_providers

        # 已经获取过直接返回
        if len(bar_providers) > 0:
            bar_provider = next((data for data in bar_providers if (data.interval == interval) & (data.bar_type == bar_type)), None)
            if bar_provider is not None:
                return bar_provider.bar_series

        # 加载历史数据
        begin_trading_date = YfTimeHelper.get_trading_day(begin_time)
        last_trading_day = YfTimeHelper.get_trading_day(end_time)
        if last_trading_day == self.trading_day:
            end_trading_date = TradingDayHelper.get_pre_trading_day(last_trading_day)
        else:
            end_trading_date = last_trading_day
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        end_time = end_trading_date + datetime.timedelta(hours=16)  # 目前国内都是15点收盘
        if bar_type == EnumBarType.second:
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date_time(self.instrument_manager, instrument_id, begin_time, end_time, interval, bar_type,
                                                          *instrument_ids)
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date_time(self.instrument_manager, instrument_id, begin_time, end_time, interval, bar_type,
                                                          *instrument_ids)
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_type == EnumBarType.day:
            bar_provider = BarProvider()
            bar_provider.create_bar_provider_by_date_time(self.instrument_manager, instrument_id, begin_time, end_time, interval, bar_type,
                                                          *instrument_ids)
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        bar_series = bar_provider.bar_series
        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, self.trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        # 组装当日数据
        self.__combine_today_tick(bar_provider, market, end_time)

        bar_providers.append(bar_provider)
        if (bar_provider.bar_type == EnumBarType.second) | (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
            lst_remove = []
            for bar in bar_provider.bar_series:
                if bar.end_time < begin_time:
                    lst_remove.append(bar)
                else:
                    break
            for bar in lst_remove:
                bar_provider.bar_series.remove(bar)
        elif bar_provider.bar_type == EnumBarType.day:
            lst_remove = []
            for bar in bar_provider.bar_series:
                if bar.end_time < begin_trading_date:
                    lst_remove.append(bar)
                else:
                    break
            for bar in lst_remove:
                bar_provider.bar_series.remove(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        return bar_provider.bar_series

    def get_bar_series_by_length(self, market, instrument_id, interval, bar_type, max_length, end_time, restore=EnumRestoration.不复权, *instrument_ids):
        """
        实盘根据回溯根数获取K线
        历史K线从历史数据直接加载组装
        当日K线根据Tick数据组装
        最后合并历史和当日K线，并返回
        注意：
        若之前已经获取过品种的K线数据，则直接从缓存返回K线，(判断条件：interval，bar_type的唯一性)
        若之前没有获取过品种的K线数据，则加载K线数据到缓存，并返回
        :param market:市场
        :param instrument_id:合约编号
        :param interval:间隔
        :param bar_type:K线类型
        :param max_length:回溯根数
        :param end_time:截止时间
        :param restore:复权方式
        :param instrument_ids:参与求交易时间交集的品种
        :return:
        """
        bar_providers = []
        if instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[instrument_id]
        else:
            self.__bar_series_map[instrument_id] = bar_providers

        # 已经获取过直接返回
        if len(bar_providers) > 0:
            bar_provider = next((data for data in bar_providers if (data.interval == interval) & (data.bar_type == bar_type)), None)
            if bar_provider is not None:
                return bar_provider.bar_series

        # 这里为了提升取数据的速度,根据时间预计算根数,不足再补
        last_trading_day = YfTimeHelper.get_trading_day(end_time)
        if last_trading_day == self.trading_day:
            end_trading_date = TradingDayHelper.get_pre_trading_day(last_trading_day)
        else:
            end_trading_date = last_trading_day
        lst_date_time_slices_one_day = BaseBarHelper.create_one_day_date_time_slice(self.instrument_manager, instrument_id, end_trading_date, interval,
                                                                                    bar_type,
                                                                                    *instrument_ids)
        if len(lst_date_time_slices_one_day) > 0:
            n_one_day_count = len(lst_date_time_slices_one_day)
        else:
            n_one_day_count = 1

        n_trading_days = int(math.ceil(max_length * 1.0 / n_one_day_count))
        if bar_type == EnumBarType.day:
            n_trading_days = n_trading_days * interval
        else:
            n_trading_days = n_trading_days

        begin_trading_date = TradingDayHelper.get_pre_trading_day(end_trading_date, n_trading_days - 1)
        lst_trading_days = TradingDayHelper.get_trading_days(begin_trading_date, end_trading_date)
        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_date_time(self.instrument_manager, instrument_id, begin_trading_date, end_trading_date, interval, bar_type,
                                                      *instrument_ids)
        if bar_provider.bar_type == EnumBarType.second:
            for trading_day in lst_trading_days:
                tick_series = self.__load_history_tick_series(market, instrument_id, trading_day)
                for tick in tick_series:
                    bar_provider.add_tick(tick)
        elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
            bar_series_min = self.load_min_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_min:
                bar_provider.add_bar(bar)
        elif bar_provider.bar_type == EnumBarType.day:
            bar_series_day = self.load_day_bar_series(market, instrument_id, begin_trading_date, end_trading_date)
            for bar in bar_series_day:
                bar_provider.add_bar(bar)
        else:
            raise Exception("不支持的k线:" + str(bar_type))

        bar_series = bar_provider.bar_series
        if len(bar_provider.bar_series) < max_length:
            trading_date = begin_trading_date
            count = 0
            while count < 5:
                count += 1
                trading_date = TradingDayHelper.get_pre_trading_day(trading_date)
                if bar_provider.bar_type == EnumBarType.second:
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    tick_series = self.__load_history_tick_series(market, instrument_id, trading_date)
                    for tick in tick_series:
                        bar_provider.add_tick(tick)
                elif (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_min = self.load_min_bar_series(market, instrument_id, trading_date)
                    for bar in bar_series_min:
                        bar_provider.add_bar(bar)
                elif bar_provider.bar_type == EnumBarType.day:
                    begin_date = TradingDayHelper.get_pre_trading_day(trading_date, interval - 1)
                    bar_provider = BarProvider()
                    bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)
                    bar_series_day = self.load_day_bar_series(market, instrument_id, begin_date, end_trading_date)
                    trading_date = begin_date
                    for bar in bar_series_day:
                        bar_provider.add_bar(bar)
                else:
                    raise Exception("不支持的k线:" + str(bar_type))

                for bar in bar_provider.bar_series:
                    bar_series.insert(0, bar)

                if len(bar_series) >= max_length:
                    break

        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, self.trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        # 组装当日数据
        self.__combine_today_tick(bar_provider, market, end_time)

        bar_providers.append(bar_provider)
        remove_length = len(bar_provider.bar_series) - max_length
        if remove_length > 0:
            del bar_provider.bar_series[0:remove_length]

        return bar_provider.bar_series

    def get_bar_series(self, market, instrument_id, interval, bar_type, end_time, bar_series, restore=EnumRestoration.不复权, *instrument_ids):
        """
        实盘根据回溯根数获取K线
        历史K线从历史数据直接加载组装
        当日K线根据Tick数据组装
        最后合并历史和当日K线，并返回
        注意：
        若之前已经获取过品种的K线数据，则直接从缓存返回K线，(判断条件：interval，bar_type的唯一性)
        若之前没有获取过品种的K线数据，则加载K线数据到缓存，并返回
        :param market:市场
        :param instrument_id:合约编号
        :param interval:间隔
        :param bar_type:K线类型
        :param end_time:截止时间
        :param restore:复权方式
        :param instrument_ids:参与求交易时间交集的品种
        :return:
        """
        bar_providers = []
        if instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[instrument_id]
        else:
            self.__bar_series_map[instrument_id] = bar_providers

        # 已经获取过直接返回
        if len(bar_providers) > 0:
            bar_provider = next((data for data in bar_providers if (data.interval == interval) & (data.bar_type == bar_type)), None)
            if bar_provider is not None:
                return bar_provider.bar_series

        bar_provider = BarProvider()
        bar_provider.create_bar_provider_by_trading_date(self.instrument_manager, instrument_id, self.trading_day, interval, bar_type, *instrument_ids)
        for bar in bar_series:
            bar_provider.bar_series.append(bar)

        # 组装当日数据
        self.__combine_today_tick(bar_provider, market, end_time)

        bar_providers.append(bar_provider)
        return bar_provider.bar_series

    def __combine_today_tick(self, bar_provider, market, end_time):
        date_time_slice = self.instrument_manager.get_living_date_time(self.trading_day, bar_provider.instrument_id)
        if end_time > date_time_slice.begin_time:
            # 加载当日数据
            tick_series = self.__load_today_tick_series(market, bar_provider.instrument_id, self.trading_day)

            if (bar_provider.bar_type == EnumBarType.second) | (bar_provider.bar_type == EnumBarType.minute) | (bar_provider.bar_type == EnumBarType.hour):
                for tick in tick_series:
                    if tick.date_time <= end_time:
                        bar_provider.add_tick(tick)
                        if tick.date_time == date_time_slice.begin_time:  # 第1个的Tick包含集合竞价信息, 特殊处理
                            bar_provider.bar_series[-1].high = tick.high_price
                            bar_provider.bar_series[-1].open = tick.open_price
                            bar_provider.bar_series[-1].low = tick.low_price
            elif bar_provider.bar_type == EnumBarType.day:
                # // 大于1不组当日日线 和MQ一致(个人认为应该组)
                if bar_provider.interval > 1:
                    return

                if (tick_series is None) | (len(tick_series) == 0):
                    return

                first_tick = tick_series[0]
                temp_tick_series = []
                for data in tick_series:
                    if data.date_time <= end_time:
                        temp_tick_series.append(data)
                if len(temp_tick_series) == 0:
                    return
                last_tick = temp_tick_series[-1]
                if (len(bar_provider.bar_series) == 0) | (bar_provider.bar_series[-1].trading_date != first_tick.trading_day):
                    bar = Bar()
                    bar.trading_date = first_tick.trading_day
                    if len(bar_provider.bar_series) == 0:
                        temp_bar = None
                    else:
                        temp_bar = bar_provider.bar_series[-1]
                    bar.open_bar(first_tick.trading_day, first_tick, temp_bar)
                    bar.turnover = first_tick.turnover
                    bar.volume = first_tick.volume
                    bar_provider.bar_series.append(bar)

                    if last_tick is None:
                        last_tick = first_tick
                    bar_provider.bar_series[-1].high = last_tick.high_price
                    bar_provider.bar_series[-1].low = last_tick.low_price
                    bar_provider.bar_series[-1].turnover = last_tick.turnover
                    bar_provider.bar_series[-1].volume = last_tick.volume
                    bar_provider.bar_series[-1].open_interest = last_tick.open_interest
                    bar_provider.bar_series[-1].end_time = last_tick.date_time
                    bar_provider.bar_series[-1].close = last_tick.last_price
                    bar_provider.bar_series[-1].trading_date = last_tick.trading_day

    def load_last_tick(self, market, instrument_id, trading_date):
        """
        获取交易日最后一个Tick
        :param market:
        :param instrument_id:
        :param trading_date:
        :return:
        """
        path = self.__future_tick_path
        try:
            file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
            file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
            if instrument_id.lower() != 'index':
                instrument = self.instrument_manager[instrument_id.split('.')[0]]
                tick_stream = BinaryTickStream(market, instrument_id, instrument.exchange_id, file_path)
                tick = tick_stream.read_last_tick()
                return tick
        except Exception as e:
            print(str(e))
            print('load_last_tick:未取到Tick数据...,请注意.....')
            return None

    def load_pre_close_by_tick(self, market, instrument_id, trading_date):
        """
        从Tick获取pre_close
        :param market:
        :param instrument_id:
        :param trading_date:
        :return:
        """
        last_tick = self.load_last_tick(market, instrument_id, trading_date)

        if last_tick is not None:
            pre_close = last_tick.pre_close_price
            if pre_close != 0:
                return pre_close
            else:
                print('pre_close:{0}为0,请注意.....'.format(pre_close))
                return pre_close
        else:
            print('load_pre_close_by_tick:未取到Tick数据,PreClose设置为0...,请注意.....')
            return 0

    def load_close_price_by_tick(self, market, instrument_id, trading_date):
        """
        从Tick获取close
        :param market:
        :param instrument_id:
        :param trading_date:
        :return:
        """
        last_tick = self.load_last_tick(market, instrument_id, trading_date)

        if last_tick is not None:
            close_price = last_tick.last_price
            if close_price != 0:
                return close_price
            else:
                print('close_price:{0}为0,请注意.....'.format(close_price))
                return close_price
        else:
            print('load_close_price_by_tick:未取到Tick数据,ClosePrice设置为0...,请注意.....')
            return 0

    def load_pre_settlement_price_by_tick(self, market, instrument_id, trading_date):
        """
        从Tick获取pre_settlement_price
        :param market:
        :param instrument_id:
        :param trading_date:
        :return:
        """
        path = self.__future_tick_path
        tick_series = []
        try:
            file_path = os.path.join(path, trading_date.strftime('%Y%m%d'))
            file_path = os.path.join(file_path, instrument_id.split('.')[0] + ".tk")
            if instrument_id.lower() != 'index':
                instrument = self.instrument_manager[instrument_id.split('.')[0]]
                tick_stream = BinaryTickStream(market, instrument_id, instrument.exchange_id, file_path)
                tick_stream.read_by_count(tick_series, 0, 5)
        except Exception as e:
            print(str(e))

        if len(tick_series) > 0:
            pre_settlement_price = tick_series[-1].pre_settlement_price
            if pre_settlement_price != 0:
                return pre_settlement_price
            else:
                print('pre_settlement_price:{0}为0,请注意.....'.format(pre_settlement_price))
                return pre_settlement_price
        else:
            print('load_pre_settlement_price_by_tick:未取到Tick数据...,请注意.....')
            return 0

    def on_bar(self, bar):
        """
        实盘on_bar维护策略获取的K线
        :param bar:
        :return:
        """
        if bar.instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[bar.instrument_id]
            for bar_provider in bar_providers:
                bar_provider.add_bar(bar)
        else:
            return

    def on_tick(self, tick):
        """
        实盘on_tick维护策略获取的K线
        :param tick:
        :return:
        """
        if tick.instrument_id in self.__bar_series_map.keys():
            bar_providers = self.__bar_series_map[tick.instrument_id]
            for bar_provider in bar_providers:
                bar_provider.add_tick(tick)
        else:
            return

    def load_min_bar_data_frame(self, market, instrument_id, *trading_dates, columns=None):
        """

        :param market:
        :param instrument_id:
        :param columns:
        :param trading_dates:
        :return:
        """
        bar_series = self.load_min_bar_series(market, instrument_id, *trading_dates)
        lst_bar = []
        for bar in bar_series:
            lst_bar.append([bar.trading_date, bar.begin_time, bar.end_time,
                            bar.high, bar.open, bar.low, bar.close, bar.volume, bar.turnover, bar.pre_close, bar.open_interest])

        df_bar = pd.DataFrame(lst_bar, columns=['trading_date', 'begin_time', 'end_time',
                                                'high', 'open', 'low', 'close', 'volume', 'turnover', 'pre_close', 'open_interest'])

        if columns is None:
            return df_bar
        else:
            return df_bar[columns]

    def load_day_bar_data_frame(self, market, instrument_id, *trading_dates, columns=None):
        """

        :param market:
        :param instrument_id:
        :param columns:
        :param trading_dates:
        :return:
        """
        bar_series = self.load_day_bar_series(market, instrument_id, *trading_dates)
        lst_bar = []
        for bar in bar_series:
            lst_bar.append([bar.trading_date, bar.begin_time, bar.end_time,
                            bar.high, bar.open, bar.low, bar.close, bar.volume, bar.turnover, bar.pre_close, bar.open_interest])

        df_bar = pd.DataFrame(lst_bar, columns=['trading_date', 'begin_time', 'end_time',
                                                'high', 'open', 'low', 'close', 'volume', 'turnover', 'pre_close', 'open_interest'])

        if columns is None:
            return df_bar
        else:
            return df_bar[columns]

    def load_tick_data_frame(self, market, instrument_id, *trading_dates, columns=None):
        """

        :param market:
        :param instrument_id:
        :param columns:['instrument_id', 'exchange_id', 'trading_date', 'local_time', 'date_time',
                                        'high_price', 'open_price', 'low_price', 'last_price', 'volume', 'turnover', 'open_interest',
                                        'bid_price1', 'bid_volume1', 'ask_price1', 'ask_volume1', 'up_limit', 'drop_limit',
                                        'pre_close_price', 'pre_settlement_price', 'pre_open_interest']
        :param trading_dates:
        :return:
        """
        tick_series = self.load_tick_series(market, instrument_id, *trading_dates)
        lst_tick = []
        for tick in tick_series:
            lst_tick.append([tick.instrument_id, tick.exchange_id, tick.trading_date, tick.local_time, tick.date_time,
                             tick.high_price, tick.open_price, tick.low_price, tick.last_price, tick.volume, tick.turnover, tick.open_interest,
                             tick.bid_price1, tick.bid_volume1, tick.ask_price1, tick.ask_volume1, tick.up_limit, tick.drop_limit,
                             tick.pre_close_price, tick.pre_settlement_price, tick.pre_open_interest])

        df_tick = pd.DataFrame(lst_tick,
                               columns=['instrument_id', 'exchange_id', 'trading_date', 'local_time', 'date_time',
                                        'high_price', 'open_price', 'low_price', 'last_price', 'volume', 'turnover', 'open_interest',
                                        'bid_price1', 'bid_volume1', 'ask_price1', 'ask_volume1', 'up_limit', 'drop_limit',
                                        'pre_close_price', 'pre_settlement_price', 'pre_open_interest'])

        if columns is None:
            return df_tick
        else:
            return df_tick[columns]

    def load_tick_data_frame_by_date_time(self, market, instrument_id, begin_time, end_time, columns=None):
        """
        根据时间区间加载历史Tick数据
        :param columns:
        :param market:市场
        :param instrument_id:合约编号
        :param begin_time:开始时间
        :param end_time:截止时间
        :return:
        """
        tick_series = self.load_tick_series_by_date_time(market, instrument_id, begin_time, end_time)
        lst_tick = []
        for tick in tick_series:
            lst_tick.append([tick.instrument_id, tick.exchange_id, tick.trading_date, tick.local_time, tick.date_time,
                             tick.high_price, tick.open_price, tick.low_price, tick.last_price, tick.volume, tick.turnover, tick.open_interest,
                             tick.bid_price1, tick.bid_volume1, tick.ask_price1, tick.ask_volume1, tick.up_limit, tick.drop_limit,
                             tick.pre_close_price, tick.pre_settlement_price, tick.pre_open_interest])

        df_tick = pd.DataFrame(lst_tick,
                               columns=['instrument_id', 'exchange_id', 'trading_date', 'local_time', 'date_time',
                                        'high_price', 'open_price', 'low_price', 'last_price', 'volume', 'turnover', 'open_interest',
                                        'bid_price1', 'bid_volume1', 'ask_price1', 'ask_volume1', 'up_limit', 'drop_limit',
                                        'pre_close_price', 'pre_settlement_price', 'pre_open_interest'])

        if columns is None:
            return df_tick
        else:
            return df_tick[columns]

    def load_bar_data_frame_by_date(self, market, instrument_id, interval, bar_type, begin_date, end_date, *instrument_ids, columns=None):
        """
        返回一个DataFrame
        :param columns:None为全选，可选列表['trading_date', 'begin_time', 'end_time', 'high', 'open',  'low', 'close', 'volume', 'turnover', 'pre_close', 'open_interest']
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param begin_date:
        :param end_date:
        :param instrument_ids:
        :return:
        """
        bar_series = self.load_bar_series_by_date(market, instrument_id, interval, bar_type, begin_date, end_date, *instrument_ids)
        lst_bar = []
        for bar in bar_series:
            lst_bar.append([bar.trading_date, bar.begin_time, bar.end_time,
                            bar.high, bar.open, bar.low, bar.close, bar.volume, bar.turnover, bar.pre_close, bar.open_interest])

        df_bar = pd.DataFrame(lst_bar, columns=['trading_date', 'begin_time', 'end_time',
                                                'high', 'open', 'low', 'close', 'volume', 'turnover', 'pre_close', 'open_interest'])

        if columns is None:
            return df_bar
        else:
            return df_bar[columns]

    def load_bar_data_frame_by_date_time(self, market, instrument_id, interval, bar_type, begin_time, end_time, *instrument_ids, columns=None):
        """

        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param begin_time:
        :param end_time:
        :param columns:
        :param instrument_ids:
        :return:
        """
        bar_series = self.load_bar_series_by_date_time(market, instrument_id, interval, bar_type, begin_time, end_time, *instrument_ids)
        lst_bar = []
        for bar in bar_series:
            lst_bar.append([bar.trading_date, bar.begin_time, bar.end_time,
                            bar.high, bar.open, bar.low, bar.close, bar.volume, bar.turnover, bar.pre_close, bar.open_interest])

        df_bar = pd.DataFrame(lst_bar, columns=['trading_date', 'begin_time', 'end_time',
                                                'high', 'open', 'low', 'close', 'volume', 'turnover', 'pre_close', 'open_interest'])

        if columns is None:
            return df_bar
        else:
            return df_bar[columns]

    def load_bar_data_frame_by_length(self, market, instrument_id, interval, bar_type, max_length, end_date, *instrument_ids, columns=None):
        """

        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param max_length:
        :param end_date:
        :param columns:
        :param instrument_ids:
        :return:
        """
        bar_series = self.load_bar_series_by_length(market, instrument_id, interval, bar_type, max_length, end_date, *instrument_ids)
        lst_bar = []
        for bar in bar_series:
            lst_bar.append([bar.trading_date, bar.begin_time, bar.end_time,
                            bar.high, bar.open, bar.low, bar.close, bar.volume, bar.turnover, bar.pre_close, bar.open_interest])

        df_bar = pd.DataFrame(lst_bar, columns=['trading_date', 'begin_time', 'end_time',
                                                'high', 'open', 'low', 'close', 'volume', 'turnover', 'pre_close', 'open_interest'])

        if columns is None:
            return df_bar
        else:
            return df_bar[columns]
