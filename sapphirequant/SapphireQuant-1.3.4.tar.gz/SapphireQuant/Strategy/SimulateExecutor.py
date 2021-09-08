import importlib
from datetime import datetime
from time import time

from SapphireQuant.Core.Futures import FutureAsset

from SapphireQuant.Config.TradingDay import TradingDayHelper

from SapphireQuant.Core.Enum import EnumSimulateMatchMode, EnumTradeEventType, EnumQuoteEventType
from SapphireQuant.DataStorage.Cache import FutureCache, FutureData
from SapphireQuant.DataStorage.Cache.FutureCache import EnumLiquidationType
from SapphireQuant.Simulate.Match.MatchCenter import MatchCenter
from SapphireQuant.Simulate.SimulateFutureQuoteChannel import SimulateFutureQuoteChannel
from SapphireQuant.Strategy.Function import Function


class SimulateExecutor:
    """
    回测执行
    """

    def __init__(self, **kwargs):
        self._debug_mode = False
        if 'debug_mode' in kwargs.keys():
            self._debug_mode = kwargs['debug_mode']

        self._start_simulate_date = kwargs['start_simulate_date']
        self._end_simulate_date = kwargs['end_simulate_date']
        self._start_simulate_date = TradingDayHelper.get_first_trading_day(self._start_simulate_date)
        self._end_simulate_date = TradingDayHelper.get_last_trading_day(self._end_simulate_date)

        self._drive_code = kwargs['drive_code']
        self._drive_bar_interval = kwargs['drive_bar_interval']
        self._drive_bar_type = kwargs['drive_bar_type']

        self._data_handler = kwargs['data_handler']
        self._future_codes = kwargs['future_codes']

        self._instrument_manager = self._data_handler.instrument_manager
        self.liquidation_type = EnumLiquidationType.收盘价
        if 'liquidation_type' in kwargs.keys():
            self.liquidation_type = kwargs['liquidation_type']

        self.product_code = kwargs['product_code']
        self.strategy_id = kwargs['strategy_id']
        self.fund_balance = kwargs['fund_balance']
        self.transaction_rate = kwargs['transaction_rate']
        self.future_long_margin_rate = kwargs['long_margin_rate']
        self.future_short_margin_rate = kwargs['short_margin_rate']
        self._match_mode = EnumSimulateMatchMode.order_price
        if 'match_mode' in kwargs.keys():
            self._match_mode = kwargs['match_mode']

        self._future_data = None

        self._strategy_path = kwargs['strategy_path']
        print('Load BaseStrategy:{0}'.format(self._strategy_path))
        module = importlib.import_module(kwargs['strategy_path'])
        if 'strategy_name' in kwargs.keys():
            strategy_name = kwargs['strategy_name']
        else:
            strategy_name = 'BaseStrategy'
        strategy_class = getattr(module, strategy_name)

        self._future_cache = FutureCache(self.transaction_rate, self.future_long_margin_rate, self.future_short_margin_rate,
                                         self._instrument_manager, self._data_handler, liquidation_type=self.liquidation_type)
        self._match_center = MatchCenter(self._future_cache, self._match_mode, self.future_long_margin_rate, self.future_short_margin_rate)

        kwargs['trade_handler'] = self._match_center
        kwargs['future_cache'] = self._future_cache
        self._function = Function(**kwargs)
        kwargs['function'] = self._function
        self._strategy = strategy_class(**kwargs)

        self._future_quote_channel = SimulateFutureQuoteChannel(self._drive_bar_interval, self._drive_bar_type,
                                                                self._start_simulate_date, self._end_simulate_date, self._data_handler, debug_mode=self._debug_mode)
        self._future_quote_channel.set_drive_code(self._drive_code)
        self._future_quote_channel.subscribe(self._future_codes)

        self._match_center.register_event(self.on_future_trade, EnumTradeEventType.on_trade)
        self._match_center.register_event(self.on_future_order, EnumTradeEventType.on_order)
        self._match_center.register_event(self.on_future_order_reject, EnumTradeEventType.on_order_reject)
        self._match_center.register_event(self.on_future_order_canceled, EnumTradeEventType.on_order_canceled)
        self._match_center.register_event(self.on_future_order_cancel_failed, EnumTradeEventType.on_order_cancel_failed)

        self._future_quote_channel.register_event(self.on_start, EnumQuoteEventType.on_start)
        self._future_quote_channel.register_event(self.on_day_begin, EnumQuoteEventType.on_day_begin)
        self._future_quote_channel.register_event(self.on_day_end, EnumQuoteEventType.on_day_end)
        self._future_quote_channel.register_event(self.on_tick, EnumQuoteEventType.on_tick)
        self._future_quote_channel.register_event(self.on_bar, EnumQuoteEventType.on_bar)
        self._future_quote_channel.register_event(self.on_end, EnumQuoteEventType.on_end)

        self._start_time = None

    def start(self):
        """
        开始
        """
        self._start_time = time()
        self._future_quote_channel.start()

    def stop(self):
        """
        停止
        """
        pass

    def on_start(self):
        """
        回测开始
        """
        print('#{0} | 复盘开始于={1}'.format(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), self._start_simulate_date.strftime('%Y/%m/%d')))
        self._strategy.on_start()

    def on_end(self):
        """
        回测结束
        """
        self._future_cache.on_end()  # 生成相应交易信息的DataFrame
        self._function.on_end()  # 初始化Function种交易信息的DataFrame、策略的Summary的DataFrame、策略的参数DataFrame
        self._strategy.on_end()  # 回测结束，调用策略的结束函数
        print('#{0} | 复盘结束于={1}'.format(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), self._end_simulate_date.strftime('%Y/%m/%d')))
        n = TradingDayHelper.get_trading_day_count(self._start_simulate_date, self._end_simulate_date)
        run_seconds = time() - self._start_time
        if n == 0:
            print('运行时间={0}秒, 平均每天={1}秒'.format(run_seconds, run_seconds))
        else:
            print('运行时间={0}秒, 平均每天={1}秒'.format(run_seconds, run_seconds / n))

    def on_day_begin(self, trading_date):
        """
        交易日开始
        :param trading_date:
        """
        begin_date = TradingDayHelper.get_first_trading_day(trading_date)
        print('#复盘{0}|开盘,交易日={1}'.format(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), trading_date.strftime('%Y/%m/%d')))
        self._function.day_begin(trading_date)
        if begin_date == trading_date:
            self._future_data = FutureData()
            self._future_data.asset = FutureAsset()
            self._future_data.asset.product_code = self.product_code
            self._future_data.asset.strategy_id = self.strategy_id
            self._future_data.asset.fund_balance = self.fund_balance
            self._future_data.asset.cash = self.fund_balance
            self._future_data.asset.available_cash = self.fund_balance
            self._future_data.asset.pre_fund_balance = self.fund_balance
            self._future_data.asset.trading_date = trading_date
            self._future_data.next_asset = self._future_data.asset
        self._future_cache.day_begin(trading_date, self._future_data)
        self._strategy.on_init()

    def on_day_end(self):
        """
        交易日结束
        """
        self._future_data = self._future_cache.day_end()

    def on_tick(self, drive_data, lst_replay_data):
        """

        :param drive_data:
        :param lst_replay_data:
        """
        self._match_center.on_tick(drive_data)
        self._match_center.match_by_tick(drive_data)

        for data in lst_replay_data:
            if data is None or data.last_price <= 0:
                continue
            self._match_center.match_by_tick(data)

        for data in lst_replay_data:
            self._future_cache.on_tick(data)
            self._function.on_tick(data)

        self._future_cache.on_tick(drive_data)

        self._function.on_tick(drive_data)
        if drive_data.instrument_id == self._function.drive_code:
            self._strategy.on_tick(drive_data)

    def on_bar(self, drive_data, lst_replay_data):
        """

        :param drive_data:
        :param lst_replay_data:
        """
        for data in lst_replay_data:
            self._future_cache.on_bar(data)
            self._function.on_bar(data)

        self._future_cache.on_bar(drive_data)
        self._function.on_bar(drive_data)
        self._strategy.on_bar(drive_data)

        self._match_center.on_bar(drive_data)
        self._match_center.match_by_bar(drive_data)

        for data in lst_replay_data:
            if data is None or data.close <= 0:
                continue
            self._match_center.match_by_bar(data)

    def on_future_trade(self, trade):
        """

        :param trade:
        """
        self._future_cache.on_trade(trade)
        self._strategy.on_future_trade(trade)

    def on_future_order(self, order):
        """

        :param order:
        """
        self._future_cache.on_order(order)
        self._strategy.on_future_order(order)

    def on_future_order_reject(self, order):
        """

        :param order:
        """
        self._future_cache.on_order_reject(order)
        self._strategy.on_future_order_reject(order)

    def on_future_order_canceled(self, order):
        """

        :param order:
        """
        self._future_cache.on_order_canceled(order)
        self._strategy.on_future_order_canceled(order)

    def on_future_order_cancel_failed(self, order_guid, msg):
        """

        :param order_guid:
        :param msg:
        """
        self._future_cache.on_order_cancel_failed(order_guid, msg)
        self._strategy.on_future_order_cancel_failed(order_guid, msg)
