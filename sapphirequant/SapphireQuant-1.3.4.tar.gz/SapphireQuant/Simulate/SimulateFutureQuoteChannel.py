import datetime

from SapphireQuant.Config.TradingDay import TradingDayHelper
from SapphireQuant.Core.Enum import EnumBarType, EnumMarket, EnumQuoteEventType
from SapphireQuant.Simulate import ReplayData


class SimulateFutureQuoteChannel:
    """
    期货回测行情通道
    """

    def __init__(self, drive_bar_interval, drive_bar_type, begin_date, end_date, data_handler, debug_mode=False):
        self._on_start_event = []
        self._on_end_event = []
        self._on_bar_event = []
        self._on_tick_event = []
        self._on_day_begin_event = []
        self._on_day_end_event = []
        self._debug_mode = debug_mode

        self._drive_bar_interval = drive_bar_interval
        self._drive_bar_type = drive_bar_type
        self.start_simulate_date = TradingDayHelper.get_first_trading_day(begin_date)
        self.end_simulate_date = TradingDayHelper.get_last_trading_day(end_date)
        self._data_handler = data_handler

        self._drive_data = None
        self._replay_data_map = {}
        self.subscribe_futures = []
        self.trading_date = self.start_simulate_date
        self.tick_now = self.start_simulate_date
        self._drive_code = None

    def set_drive_code(self, drive_code):
        """

        :param drive_code:
        """
        self._drive_code = drive_code
        self._drive_data = ReplayData(drive_code)
        if self._drive_code not in self.subscribe_futures:
            self.subscribe_futures.append(self._drive_code)

    def subscribe(self, instruments):
        """
        订阅
        :param instruments:
        """
        for future_code in instruments:
            if len(future_code) == 0:
                continue

            if future_code not in self.subscribe_futures:
                self.subscribe_futures.append(future_code)

            if future_code == self._drive_code:
                continue

            if future_code not in self._replay_data_map.keys():
                self._replay_data_map[future_code] = ReplayData(future_code)

    def start(self):
        """
        开始播放
        """
        if self._drive_bar_type == EnumBarType.day:
            # 初始化数据
            for instrument_id in self.subscribe_futures:
                bar_series = self._data_handler.load_bar_series_by_date(
                    EnumMarket.期货, instrument_id, self._drive_bar_interval, self._drive_bar_type, self.start_simulate_date, self.end_simulate_date)
                if instrument_id == self._drive_code:
                    for bar in bar_series:
                        self._drive_data.add_data(bar.trading_date, [bar])
                else:
                    for bar in bar_series:
                        self._replay_data_map[instrument_id].add_data(bar.trading_date, [bar])

            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self._data_handler.init(trading_date)
                self.__replay_bar(trading_date)
            self.on_end()
        elif (self._drive_bar_type == EnumBarType.minute) or (self._drive_bar_type == EnumBarType.hour):
            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self._data_handler.init(trading_date)

                for instrument_id in self.subscribe_futures:
                    bar_series = self._data_handler.load_bar_series_by_date(
                        EnumMarket.期货, instrument_id, self._drive_bar_interval, self._drive_bar_type, trading_date, trading_date)
                    if instrument_id == self._drive_code:
                        self._drive_data.add_data(trading_date, bar_series)
                    else:
                        self._replay_data_map[instrument_id].add_data(trading_date, bar_series)

                self.__replay_bar(trading_date)
            self.on_end()
        elif self._drive_bar_type == EnumBarType.tick:
            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self._data_handler.init(trading_date)

                for instrument_id in self.subscribe_futures:
                    tick_series = self._data_handler.load_tick_series(EnumMarket.期货, instrument_id, trading_date)
                    if instrument_id == self._drive_code:
                        self._drive_data.add_data(trading_date, tick_series)
                    else:
                        self._replay_data_map[instrument_id].add_data(trading_date, tick_series)

                self.__replay_tick(trading_date)
            self.on_end()
        elif self._drive_bar_type == EnumBarType.night_am_pm:
            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self._data_handler.init(trading_date)

                for instrument_id in self.subscribe_futures:
                    bar_series = self._data_handler.load_night_am_pm_bar_series_by_date(
                        EnumMarket.期货, instrument_id, self._drive_bar_interval, self._drive_bar_type, trading_date, trading_date)
                    if instrument_id == self._drive_code:
                        self._drive_data.add_data(trading_date, bar_series)
                    else:
                        self._replay_data_map[instrument_id].add_data(trading_date, bar_series)

                self.__replay_bar(trading_date)
            self.on_end()

    def __replay_bar(self, trading_date):
        """
        播放bar
        :param trading_date:
        """
        self._drive_data.current_trading_date = trading_date
        for replay_data in self._replay_data_map.values():
            replay_data.current_trading_date = trading_date

        if trading_date in self._drive_data.data_block_map.keys():
            drive_data_series = self._drive_data.data_block_map[trading_date].data_list
        else:
            print('{0}@{1},缺失数据'.format(self._drive_code, self.trading_date))
            self.on_day_begin(self.trading_date)
            self.on_day_end()
            return

        trading_date = drive_data_series[0].trading_date
        self.on_day_begin(trading_date)
        for drive_data in drive_data_series:
            drive_data.instrument_id = self._drive_code
            self.tick_now = drive_data.end_time

            lst_replay_data = []
            for key in self._replay_data_map.keys():
                res = self._replay_data_map[key].replay_bar_to_time(self.tick_now)
                lst_replay_data = res[1]
                if res[0]:
                    for replay_data in lst_replay_data:
                        replay_data.instrument_id = key
            self.on_bar(drive_data, lst_replay_data)

        self.on_day_end()

    def __replay_tick(self, trading_date):
        """
        播放tick
        :param trading_date:
        """
        self._drive_data.current_trading_date = trading_date
        for replay_data in self._replay_data_map.values():
            replay_data.current_trading_date = trading_date

        if trading_date in self._drive_data.data_block_map.keys():
            drive_data_series = self._drive_data.data_block_map[trading_date].data_list
        else:
            print('{0}@{1},缺失数据'.format(self._drive_code, self.trading_date))
            self.on_day_begin(self.trading_date)
            self.on_day_end()
            return

        trading_date = drive_data_series[0].trading_date
        self.on_day_begin(trading_date)
        for drive_data in drive_data_series:
            drive_data.instrument_id = self._drive_code
            self.tick_now = drive_data.date_time

            lst_replay_data = []
            for key in self._replay_data_map.keys():
                res = self._replay_data_map[key].replay_tick_to_time(self.tick_now)
                lst_replay_data = res[1]
                if res[0]:
                    for replay_data in lst_replay_data:
                        replay_data.instrument_id = key
            self.on_tick(drive_data, lst_replay_data)

        self.on_day_end()

    def on_start(self):
        """
        回测开始
        """
        try:
            for event in self._on_start_event:
                event()
        except Exception as e:
            print('回测行情模块：[on_start]事件异常:{0}'.format(str(e)))
            if self._debug_mode:
                raise e

    def on_day_begin(self, trading_date):
        """
        交易日开始
        :param trading_date:
        """
        try:
            for event in self._on_day_begin_event:
                event(trading_date)
        except Exception as e:
            print('回测行情模块：[on_day_begin]事件异常:{0}'.format(str(e)))
            if self._debug_mode:
                raise e

    def on_day_end(self):
        """
        交易日结束
        """
        try:
            for event in self._on_day_end_event:
                event()
        except Exception as e:
            print('回测行情模块：[on_day_end]事件异常:{0}'.format(str(e)))
            if self._debug_mode:
                raise e

    def on_tick(self, drive_tick, lst_replay_tick):
        """
        on_tick触发
        :param lst_replay_tick:
        :param drive_tick:
        """
        try:
            for event in self._on_tick_event:
                event(drive_tick, lst_replay_tick)
        except Exception as e:
            print('回测行情模块：[on_tick]事件异常:{0}'.format(str(e)))
            if self._debug_mode:
                raise e

    def on_bar(self, drive_bar, lst_replay_bar):
        """
        OnBar触发
        :param lst_replay_bar: 其他Bar
        :param drive_bar:驱动Bar
        """
        try:
            for event in self._on_bar_event:
                event(drive_bar, lst_replay_bar)
        except Exception as e:
            print('回测行情模块：[on_bar]事件异常:{0}'.format(str(e)))
            if self._debug_mode:
                raise e

    def on_end(self):
        """
        回测结束
        """
        try:
            for event in self._on_end_event:
                event()
        except Exception as e:
            print('回测行情模块：[on_end]事件异常:{0}'.format(str(e)))
            if self._debug_mode:
                raise e

    def register_event(self, event, event_type):
        """
        注册事件
        :param event_type:
        :param event:EnumQuoteEventType
        """
        if event_type == EnumQuoteEventType.on_start:
            self._on_start_event.append(event)
        elif event_type == EnumQuoteEventType.on_end:
            self._on_end_event.append(event)
        elif event_type == EnumQuoteEventType.on_day_begin:
            self._on_day_begin_event.append(event)
        elif event_type == EnumQuoteEventType.on_day_end:
            self._on_day_end_event.append(event)
        elif event_type == EnumQuoteEventType.on_bar:
            self._on_bar_event.append(event)
        elif event_type == EnumQuoteEventType.on_tick:
            self._on_tick_event.append(event)