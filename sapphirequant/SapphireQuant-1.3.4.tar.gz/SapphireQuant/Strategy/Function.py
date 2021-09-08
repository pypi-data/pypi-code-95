from datetime import datetime, timedelta

from SapphireQuant.Config.TradingDay import TradingDayHelper

from SapphireQuant.Config.TradingFrame import FutureTradingTime
from SapphireQuant.Core.Enum import EnumMarket, EnumOrderPriceType, EnumOrderStatus, EnumOrderRejectReason, EnumOrderType, EnumHedgeFlag, EnumStrategyWorkMode, EnumBuySell, EnumOpenClose, \
    EnumPositionDirection, EnumPositionType
from SapphireQuant.Core.Futures import FutureOrder
from SapphireQuant.Strategy import StrategyToolBox
import pandas as pd


class Function:
    """
    方法句柄
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.data_handler = kwargs['data_handler']
        self._trade_handler = kwargs['trade_handler']

        self.instrument_manager = self.data_handler.instrument_manager
        self.fund_balance = kwargs['fund_balance']
        self._future_codes = kwargs['future_codes']
        self._drive_code = kwargs['drive_code']
        self._work_mode = EnumStrategyWorkMode.simulate
        self._start_simulate_date = kwargs['start_simulate_date']
        self._end_simulate_date = kwargs['end_simulate_date']
        self._start_simulate_date = TradingDayHelper.get_first_trading_day(self._start_simulate_date)
        self._end_simulate_date = TradingDayHelper.get_last_trading_day(self._end_simulate_date)

        if 'work_mode' in kwargs.keys():
            self._work_mode = kwargs['work_mode']

        self.all_futures = {}
        self._gen_future_series(self._future_codes)

        self._indicators = []
        self.future_trading_time = None
        self._trading_date = None
        self._now = self._start_simulate_date
        self._last_bar_map = {}

        self.df_asset = None
        self.df_order = None
        self.df_trade = None
        self.df_position = None
        self.df_position_detail = None

        self.df_summary = None
        self.df_param = None
        self.lst_summary = None

        self.trading_day_num = None
        self.total_trade_lots = None
        self.volume_per_day = None
        self.yield_rate = None
        self.total_yield_rate = None
        self.annual_yield_rate = None
        self.profit_per_hand = None
        self.max_retrace_rate = None
        self.retrace_ratio = None
        self.sharpe_ratio = None

    def day_begin(self, trading_date):
        """

        :param trading_date:
        """
        self._trading_date = trading_date
        self.data_handler.trading_day = trading_date
        lst_time_slices = self.get_trading_time(self._drive_code)
        self.future_trading_time = FutureTradingTime(self._drive_code, self._trading_date, lst_time_slices)
        if self.future_trading_time.if_night_flag:
            self._now = self.future_trading_time.night_open + timedelta(minutes=-1)
        else:
            self._now = self.future_trading_time.day_am_open + timedelta(minutes=-1)

    def day_end(self):
        """
        交易日结束
        """

    def add_indicator(self, indicator):
        """

        :param indicator:
        """
        indicator.calculate()
        self._indicators.append(indicator)

    def get_trading_time(self, instrument_id):
        """
        获取品种当日的交易区间
        :param instrument_id:
        :return:
        """
        return self.instrument_manager.get_trading_time(self._trading_date, instrument_id)

    @property
    def last_bar_map(self):
        """

        :return:
        """
        return self._last_bar_map

    @property
    def trading_date(self):
        """
        交易日
        :return:
        """
        return self._trading_date

    @property
    def drive_code(self):
        """
        触发品种
        :return:
        """
        return self._drive_code

    @property
    def start_simulate_date(self):
        """

        :return:
        """
        return self._start_simulate_date

    @property
    def end_simulate_date(self):
        """

        :return:
        """
        return self._end_simulate_date

    @property
    def now(self):
        """
        当前时间
        :return:
        """
        return self._now

    def _gen_future_series(self, future_codes):
        for instrument_id in future_codes:
            if instrument_id not in self.all_futures.keys():
                self.all_futures[instrument_id] = self.instrument_manager[instrument_id]

    def on_tick(self, tick):
        """
        Tick触发
        :param tick:
        """
        self._now = tick.date_time
        self.data_handler.on_tick(tick)
        instrument_id = tick.instrument_id.split('.')[0]
        self.all_futures[instrument_id].last_tick = tick
        if self._work_mode == EnumStrategyWorkMode.simulate:
            if self._drive_code in tick.instrument_id:
                for indicator in self._indicators:
                    indicator.calculate()
        else:
            for indicator in self._indicators:
                indicator.calculate()

    def on_bar(self, bar):
        """
        Bar触发
        :param bar:
        """
        self._now = bar.begin_time
        self._last_bar_map[bar.instrument_id] = bar
        self.data_handler.on_bar(bar)
        if self._work_mode == EnumStrategyWorkMode.simulate:
            if self._drive_code in bar.instrument_id:
                for indicator in self._indicators:
                    indicator.calculate()
        else:
            for indicator in self._indicators:
                indicator.calculate()

    def get_bar_series_by_date_time(self, market, instrument_id, interval, bar_type, begin_time):
        """
        根据时间获取K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param begin_time:
        :return:
        """
        return self.data_handler.get_bar_series_by_date_time(market, instrument_id, interval, bar_type, begin_time, self._now)

    def get_bar_series_by_length(self, market, instrument_id, interval, bar_type, max_length) -> object:
        """
        根据回溯根数获取K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param max_length:
        :return:
        """
        return self.data_handler.get_bar_series_by_length(market, instrument_id, interval, bar_type, max_length, self._now)

    def send_future_order(self, logic_account_name, task_guid, product_code, strategy_id,
                          instrument_id, exchange_id, price, volume, direction, open_close,
                          price_type=EnumOrderPriceType.限价,
                          # time_force = EnumOrderTimeForce.当日有效,
                          hedge_flag=EnumHedgeFlag.投机,
                          order_time=None):
        """
        发送委托
        :param order_time:
        :param logic_account_name:
        :param task_guid:
        :param product_code:
        :param strategy_id:
        :param instrument_id:
        :param exchange_id:
        :param price:
        :param volume:
        :param direction:
        :param open_close:
        :param price_type:
        :param hedge_flag:
        """
        order = FutureOrder()
        order.order_sys_id = ''
        order.product_code = product_code
        order.strategy_id = strategy_id
        order.task_guid = task_guid
        order.instrument_id = instrument_id
        order.instrument_name = ''
        order.instrument_type = EnumMarket.期货
        order.exchange_id = exchange_id
        order.direction = direction
        order.open_close = open_close
        order.hedge_flag = hedge_flag
        order.order_status = EnumOrderStatus.未知
        order.price_type = price_type
        order.broker_id = ''
        order.investor_id = ''
        order.user_id = ''
        # order.time_force = time_force
        order.order_volume = volume
        order.order_price = price
        if order_time is not None:
            order.order_time = order_time

        order.volume_traded = 0
        order.volume_canceled = 0
        order.cancel_time = None

        order.order_reject_reason = EnumOrderRejectReason.未知
        order.match_price = 0
        order.match_amount = 0
        order.frozen_amount = 0
        order.transaction_cost = 0
        order.order_type = EnumOrderType.normal
        order.local_order_time = None
        order.status_msg = ''
        order.remark = ''
        return self._trade_handler.send_future_order(logic_account_name, order)

    def get_future_position(self, logic_account_name, product_code, strategy_id, instrument_id, direction):
        """
        获取期货持仓
        :param logic_account_name:
        :param product_code:
        :param strategy_id:
        :param instrument_id:
        :param direction:
        """
        self._trade_handler.get_future_position(logic_account_name, product_code, strategy_id, instrument_id, direction)

    def on_end(self):
        """
        生成策略报告
        """
        self.df_asset = self._trade_handler.get_all_future_assets()
        self.df_order = self._trade_handler.get_all_future_orders()
        self.df_trade = self._trade_handler.get_all_future_trades()
        self.df_position = self._trade_handler.get_all_future_positions()
        self.df_position_detail = self._trade_handler.get_all_future_position_details()

        self.trading_day_num = TradingDayHelper.get_trading_day_count(self.start_simulate_date, self.end_simulate_date)
        self.total_trade_lots = self.df_trade['量'].sum() / 2
        self.volume_per_day = self.total_trade_lots / len(self.df_asset)
        self.yield_rate = StrategyToolBox.calc_total_and_annual_yield_rate(self.df_asset, self.fund_balance, 243, self.trading_day_num)
        self.total_yield_rate = self.yield_rate[0]
        self.annual_yield_rate = self.yield_rate[1]
        self.profit_per_hand = StrategyToolBox.calc_profit_per_hand(self.df_asset, self.total_trade_lots)
        self.max_retrace_rate = StrategyToolBox.calc_max_retrace_rate(self.df_asset, self.fund_balance)
        self.retrace_ratio = StrategyToolBox.calc_retrace_ratio(self.max_retrace_rate, self.annual_yield_rate)
        self.sharpe_ratio = StrategyToolBox.calc_sharpe_ratio(self.df_asset, self.fund_balance)
        self.lst_summary = [
            [self.drive_code, self.start_simulate_date, self.end_simulate_date, self.trading_day_num, self.total_trade_lots, self.volume_per_day,
             self.total_yield_rate, self.annual_yield_rate, self.profit_per_hand, self.max_retrace_rate, self.retrace_ratio, self.sharpe_ratio]]
        self.df_summary = pd.DataFrame(self.lst_summary, columns=['品种', '开始日期', '截止日期', '交易天数', '总手数', '日均手数',
                                                                  '总收益', '年化收益', '每手盈利', '最大回撤', '收益回撤比', '夏普率'])

        lst_param = []
        for key in self.kwargs:
            if key not in ['factor_map', 'data_handle', 'mongodb_client']:
                lst_param.append([key, str(self.kwargs[key])])
        self.df_param = pd.DataFrame(lst_param, columns=['参数名', '参数值'])
