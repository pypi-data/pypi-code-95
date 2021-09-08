import datetime
import string
import threading
from collections import defaultdict

from SapphireQuant import Tick
from SapphireQuant.Core import QiEvent

from SapphireQuant.Core.Bar import Bar
from SapphireQuant.Core.BarSeries import BarSeries
from SapphireQuant.Core.Enum.EnumBarType import EnumBarType
from SapphireQuant.Core.QiEvent import HandlerType
from SapphireQuant.DataProcessing.BaseBarHelper import BaseBarHelper

EVENT_BAR_OPEN = "eBarOpen."
EVENT_BAR_CLOSE = "eBarClose."


class BarProvider:
    """
    K线提供器
    """

    def __init__(self):
        self._bar_series: BarSeries = BarSeries()
        self._lst_date_time_slices: list = []
        self._pos_time: int = 0
        self._pos_bar: int = -1
        self._last_tick: Tick = None
        self._diff_time_span: datetime = datetime.timedelta(0, 0, 0)
        self._trading_date: datetime = datetime.datetime(1990, 1, 1, 0, 0, 0)
        self._is_supplement_blank_bar: bool = False
        self._enable_live: bool = False
        self._change_state = 0  # 0-没有barOpen,barClose,有更新;1-barClose;2-barOpen;3-barClose/barOpen;4-没有更新
        self.instrument_id: string = ""
        self._interval: int = 0
        self.bar_type: EnumBarType = EnumBarType.minute
        self._handlers: defaultdict = defaultdict(list)  # 暂时先不用，后面有需求再放开，通过线程来处理事件，参考vn.py

        self._lock = threading.RLock()

    def register(self, type: str, handler: HandlerType) -> None:
        """
        Register a new handler function for a specific event type. Every
        function can only be registered once for each event type.
        """
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        Unregister an existing handler function from event engine.
        """
        handler_list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(type)

    def create_bar_provider_by_date_time(self, instrument_manager, instrument_id, begin_time, end_time, interval, bar_type, *instrument_ids):
        """
        根据时间区间创建K线提供器
        :param instrument_manager:
        :param instrument_id:
        :param begin_time:
        :param end_time:
        :param interval:
        :param bar_type:
        :param instrument_ids:
        """
        self.instrument_id = instrument_id
        self._interval = interval
        self.bar_type = bar_type
        if (bar_type == EnumBarType.second) | (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            self._lst_date_time_slices = BaseBarHelper.create_in_day_date_time_slice_by_date_time(instrument_manager, instrument_id, begin_time, end_time, interval, bar_type, *instrument_ids)
        elif bar_type == EnumBarType.day:
            self._lst_date_time_slices = BaseBarHelper.create_out_day_date_time_slice_by_date_time(begin_time, end_time, interval, bar_type)
        else:
            raise Exception("不支持的K线类型")

    def create_bar_provider_by_trading_date(self, instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids):
        """
        根据交易日创建K线提供器
        :param instrument_manager:
        :param instrument_id:
        :param trading_date:
        :param interval:
        :param bar_type:
        :param instrument_ids:
        """
        self.instrument_id = instrument_id
        self._interval = interval
        self.bar_type = bar_type
        self._lst_date_time_slices = BaseBarHelper.create_one_day_date_time_slice(instrument_manager, instrument_id, trading_date, interval, bar_type, *instrument_ids)

    def create_bar_provider_by_date(self, instrument_manager, instrument_id, begin_date, end_date, interval, bar_type, *instrument_ids):
        """
        根据日期区间创建K线提供器
        :param instrument_manager:
        :param instrument_id:
        :param begin_date:
        :param end_date:
        :param interval:
        :param bar_type:
        :param instrument_ids:
        """
        self.instrument_id = instrument_id
        self._interval = interval
        self.bar_type = bar_type
        if (bar_type == EnumBarType.second) | (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            self._lst_date_time_slices = BaseBarHelper.create_in_day_date_time_slice_by_date(instrument_manager, instrument_id, begin_date,
                                                                                             end_date, interval,
                                                                                             bar_type, *instrument_ids)
        elif bar_type == EnumBarType.day:
            self._lst_date_time_slices = BaseBarHelper.create_out_day_date_time_slice_by_date(begin_date, end_date, interval, bar_type)
        else:
            raise Exception("不支持的K线类型")

    def create_bar_provider_by_date_24h(self, begin_date, end_date, interval, bar_type):
        """
        根据日期区间创建K线提供器
        :param begin_date:
        :param end_date:
        :param interval:
        :param bar_type:
        """
        self._interval = interval
        self.bar_type = bar_type
        if (bar_type == EnumBarType.second) | (bar_type == EnumBarType.minute) | (bar_type == EnumBarType.hour):
            self._lst_date_time_slices = BaseBarHelper.create_in_day_date_time_slice_by_date_24h(begin_date,
                                                                                                 end_date, interval,
                                                                                                 bar_type)
        elif bar_type == EnumBarType.day:
            self._lst_date_time_slices = BaseBarHelper.create_out_day_date_time_slice_by_date(begin_date, end_date, interval, bar_type)
        else:
            raise Exception("不支持的K线类型")

    def create_night_am_pm_bar_provider_by_date(self, instrument_manager, instrument_id, begin_date, end_date, *instrument_ids):
        """
        根据日期区间创建K线提供器,只切分夜盘 上午盘 下午盘
        :param instrument_manager:
        :param instrument_id:
        :param begin_date:
        :param end_date:
        :param instrument_ids:
        """
        self.instrument_id = instrument_id
        self._interval = 1
        self.bar_type = EnumBarType.hour
        self._lst_date_time_slices = BaseBarHelper.create_night_am_pm_date_time_slice_by_date(instrument_manager, instrument_id, begin_date, end_date, *instrument_ids)

    @property
    def is_end(self):
        """
        是否结束
        :return:
        """
        return self._pos_time >= len(self._lst_date_time_slices)

    @property
    def bar_series(self):
        """
        K线
        :return:
        """
        return self._bar_series

    @property
    def date_time_slices(self):
        return self._lst_date_time_slices

    def add_bar(self, new_bar):
        """
        添加bar
        :param new_bar:
        :return:
        """
        if new_bar is None:
            self._change_state = 4
            return

        self._lock.acquire()
        try:
            if self.is_end:
                self._change_state = 4
                return
            result = self.__move_to(new_bar.begin_time, new_bar.end_time)
            ir = result[0]
            index = result[1]
            if ir == -1:
                self._change_state = 4
                return
            bar_open_count = 0
            bar_close_count = 0
            while self._pos_time < index:
                if self._pos_bar == self._pos_time:
                    pass
                else:
                    self._pos_bar += 1

                self._pos_time += 1
            if ir == 0:
                if self._pos_bar == self._pos_time:
                    bar = self.bar_series[-1]
                    bar.add_bar(new_bar)
                else:
                    bar = Bar()
                    bar.trading_date = new_bar.trading_date
                    bar.open_bar_with_new_bar(new_bar)
                    self.bar_series.append(bar)

                    bar_open_count += 1

                    # OnBarOpened(bar)

                    self._pos_bar += 1

                    current_date_time_slice = self._lst_date_time_slices[self._pos_time]
                    if new_bar.end_time >= current_date_time_slice.end_time:
                        bar_close_count += 1

                        self.bar_series[-1].close_bar(current_date_time_slice.end_time)
                        # (BarSeries.Last)

                if (bar_open_count == 0) & (bar_close_count == 0):
                    self._change_state = 0
                    return

                if bar_open_count > bar_close_count:
                    self._change_state = 2
                    return

                if bar_close_count > bar_open_count:
                    self._change_state = 1
                    return

                self._change_state = 3
        except Exception as e:
            print('Add Bar Error')
        finally:
            self._lock.release()

    def add_tick(self, tick):
        """
        添加Tick
        :param tick:
        :return:
        """
        if tick is None:
            self._change_state = 4
            return

        turnover = 0
        volume = 0
        self._trading_date = tick.trading_date

        self._lock.acquire()
        try:
            # 第一个tick
            if self._last_tick is not None:
                turnover = self._last_tick.turnover
                volume = self._last_tick.volume
            else:
                if self._enable_live:
                    self._diff_time_span = tick.date_time - datetime.datetime.now()
                for bar in self.bar_series:
                    if bar.trading_date == self._trading_date:
                        turnover = turnover + bar.turnover
                        volume = volume + bar.volume

            if self.is_end:
                self._change_state = 4
                return

            result = self.__move_to(tick.date_time, tick.date_time)  # 自动判断是否切换下个区间
            ir = result[0]
            index = result[1]
            if ir == -1:
                self._change_state = 4
                return

            self._last_tick = tick

            bar_open_count = 0
            bar_close_count = 0
            while self._pos_time < index:
                current_t = self._lst_date_time_slices[self._pos_time]

                if self._pos_bar == self._pos_time:
                    bar_close_count += 1

                    self.bar_series[-1].close_bar(current_t.end_time)
                    # OnBarClosed(BarSeries.Last)
                else:
                    # 20150628 去掉空Bar
                    if self._is_supplement_blank_bar:
                        bar_open_count += 1
                        bar = Bar()
                        bar.begin_time = current_t.begin_time
                        if self._pos_bar >= 0:
                            bar.close = bar.pre_close = bar.open = bar.high = bar.low = self.bar_series[-1].close
                            bar.open_interest = self.bar_series[-1].open_interest
                        elif self._last_tick is not None:
                            if self._last_tick.pre_settlement_price > 0:
                                bar.close = bar.pre_close = bar.open = bar.high = bar.low = self._last_tick.pre_settlement_price
                            else:
                                bar.close = bar.pre_close = bar.open = bar.high = bar.low = self._last_tick.pre_close_price

                            bar.open_interest = self._last_tick.pre_open_interest

                        bar.trading_date = tick.trading_day
                        self.bar_series.append(bar)

                        bar_close_count += 1
                        self.bar_series[-1].close_bar(current_t.end_time)
                        # OnBarClosed(BarSeries.Last)
                    self._pos_bar += 1

                self._pos_time += 1

            # 有效的
            if ir == 0:
                if self._pos_bar == self._pos_time:
                    bar = self.bar_series[-1]
                    bar.add_tick(tick)
                    bar.turnover = bar.turnover + tick.turnover - turnover
                    bar.volume = bar.volume + tick.volume - volume
                else:
                    if len(self.bar_series) == 0:
                        last_bar = None
                    else:
                        last_bar = self.bar_series[-1]
                    bar = Bar()
                    bar.trading_date = self._trading_date
                    bar.open_bar(self._lst_date_time_slices[self._pos_time].begin_time, tick, last_bar)
                    if last_bar is not None:
                        bar.turnover = tick.turnover - turnover
                        bar.volume = tick.volume - volume
                    else:
                        bar.turnover = tick.turnover
                        bar.volume = tick.volume

                    self.bar_series.append(bar)

                    bar_open_count += 1
                    # OnBarOpened(bar)

                    self._pos_bar += 1

            if (bar_open_count == 0) & (bar_close_count == 0):
                self._change_state = 0
                return

            if bar_open_count > bar_close_count:
                self._change_state = 2
                return

            if bar_close_count > bar_open_count:
                self._change_state = 1
                return

            self._change_state = 3
        except Exception as e:
            print(e)
        finally:
            self._lock.release()

    def __move_to(self, begin_time, end_time):
        index = self._pos_time

        # region -1 无效
        current_date_time_slice = self._lst_date_time_slices[self._pos_time]
        if begin_time < current_date_time_slice.begin_time:
            return -1, index
        # endregion

        # region 1 下一个
        while index < len(self._lst_date_time_slices) - 1:
            date_time_slice = self._lst_date_time_slices[index]
            next_date_time_slice = self._lst_date_time_slices[index + 1]

            ir = self.__is_current_date_time_slice(date_time_slice, next_date_time_slice, begin_time, end_time)
            if ir == 0:
                return 0, index
            # 处理盘中休息的异常数据(一般不会出现这种情况)
            if ir == 2:
                index += 1
                return 0, index
            index += 1

        # 收盘以后的Tick处理
        bmy = self.__is_current_date_time_slice(self._lst_date_time_slices[index], None, begin_time, end_time)
        if bmy == 0:
            return 0, index

        index += 1

        # endregion

        return 1, index

    @staticmethod
    def __is_current_date_time_slice(current_date_time_slice, next_date_time_slice, begin_time, end_time):
        if next_date_time_slice is not None:
            if current_date_time_slice.end_time < next_date_time_slice.begin_time:
                if (begin_time > current_date_time_slice.end_time) & (begin_time < next_date_time_slice.begin_time):
                    ta = begin_time - current_date_time_slice.end_time
                    tb = next_date_time_slice.begin_time - begin_time
                    if tb.total_seconds() < ta.total_seconds():
                        return 2
                    return 0

            if (current_date_time_slice.begin_time <= begin_time) & (begin_time < next_date_time_slice.begin_time):
                return 0
        else:
            # 收盘5秒内的tick都计算
            if (current_date_time_slice.begin_time <= begin_time) & (end_time < (current_date_time_slice.end_time + datetime.timedelta(seconds=59))):
                return 0
        return 1

    def _process(self, event: QiEvent) -> None:
        """
        First ditribute event to those handlers registered listening
        to this type.
        """
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]
