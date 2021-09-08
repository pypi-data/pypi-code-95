import abc
import datetime
import os
import time

import pandas as pd

from SapphireQuant.Config.TradingDay import TradingDayHelper
from SapphireQuant.Core.Enum import EnumBuySell, EnumOpenClose, EnumPositionDirection, EnumBarType, EnumMarket, EnumPositionType
from SapphireQuant.Core.Futures import FutureAsset, FutureOrder, FutureTrade
from SapphireQuant.DataStorage.Cache import FutureData, FutureCache
from SapphireQuant.DataStorage.Cache.FutureCache import EnumLiquidationType
from SapphireQuant.Lib import FileToolBox
from SapphireQuant.Simulate import ReplayData
from SapphireQuant.Strategy.StrategyToolBox import StrategyToolBox


class OldStrategy:
    """
    策略基类 不带Function,不带撮合机的
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if 'mongodb_client' in kwargs.keys():
            self.mongodb_client = kwargs['mongodb_client']
        else:
            self.mongodb_client = None
        if 'record_dir' in kwargs.keys():
            self.record_dir = kwargs['record_dir']
        else:
            self.record_dir = None
        self.product_code = kwargs['product_code']
        self.strategy_id = kwargs['strategy_id']
        self.tick_now = None
        self.last_bar = None
        self.last_tick = None
        self.future_data = None
        self.drive_code = kwargs['drive_code']
        self.subscribe_futures = kwargs['subscribe_futures']
        self.drive_bar_interval = kwargs['drive_bar_interval']
        self.drive_bar_type = kwargs['drive_bar_type']
        self.start_simulate_date = kwargs['start_simulate_date']
        self.end_simulate_date = kwargs['end_simulate_date']
        self.trading_date = self.start_simulate_date
        self.data_handler = kwargs['data_handler']
        self.fund_balance = kwargs['fund_balance']
        self.instrument_manager = self.data_handler.instrument_manager
        self.transaction_rate = kwargs['transaction_rate']
        self.long_margin_rate = kwargs['long_margin_rate']
        self.short_margin_rate = kwargs['short_margin_rate']

        self.liquidation_type = EnumLiquidationType.收盘价
        if 'liquidation_type' in kwargs.keys():
            self.liquidation_type = kwargs['liquidation_type']

        self.future_cache = FutureCache(self.transaction_rate, self.long_margin_rate, self.short_margin_rate,
                                        self.data_handler.instrument_manager, self.data_handler, liquidation_type=self.liquidation_type)

        self.all_futures = {}

        self.drive_replay_data = ReplayData(self.drive_code)
        self.other_replay_data_map = {}
        self.last_bar_map = {}
        self.subscribe(self.subscribe_futures)

        self.all_assets = []
        self.all_orders = []
        self.all_trades = []
        self.all_positions = []
        self.all_position_details = []

        self.df_asset = None
        self.lst_asset = []

        self.df_order = None
        self.lst_order = []

        self.df_trade = None
        self.lst_trade = []

        self.df_position = None
        self.lst_position = []

        self.df_position_detail = None
        self.lst_position_detail = []

        self.df_summary = None
        self.df_summary_by_year = None
        self.df_summary_filter = None
        self.df_param = None
        self.run_seconds = 0.0
        self.indicators = []

        self.trading_day_num = None
        self.total_trade_lots = None
        self.volume_per_day = None
        self.yield_rate = None
        self.total_yield_rate = None
        self.annual_yield_rate = None
        self.profit_per_hand = None
        self.max_retrace_rate = None
        self.max_retrace = None
        self.retrace_ratio = None
        self.sharpe_ratio = None
        self.max_daily_loss = None
        self.continuous_innovation_high_days = None
        self.max_loss_days = None
        self.lst_summary = None

        self.is_allow = True  # 主要用来管理已跑过的策略自动不执行
        self.order_sys_id = -1
        self.trade_sys_id = -1

    def add_indicator(self, indicator):
        """
        添加指标
        :param indicator:
        """
        indicator.calculate()
        self.indicators.append(indicator)

    def subscribe(self, instrument_ids):
        """
        订阅品种
        :param instrument_ids:合约代码ID序列
        """
        for instrument_id in instrument_ids:
            if instrument_id not in self.all_futures.keys():
                self.all_futures[instrument_id] = self.instrument_manager[instrument_id]
                if instrument_id != self.drive_code:
                    self.other_replay_data_map[instrument_id] = ReplayData(instrument_id)
                self.last_bar_map[instrument_id] = None

    def start_simulate(self):
        """
        开始回测
        """
        t0 = time.time()
        if self.drive_bar_type == EnumBarType.day:
            # 初始化数据
            for instrument_id in self.subscribe_futures:
                bar_series = self.data_handler.load_bar_series_by_date(
                    EnumMarket.期货, instrument_id, self.drive_bar_interval, self.drive_bar_type, self.start_simulate_date, self.end_simulate_date)
                if instrument_id == self.drive_code:
                    for bar in bar_series:
                        self.drive_replay_data.add_data(bar.trading_date, [bar])
                else:
                    for bar in bar_series:
                        self.other_replay_data_map[instrument_id].add_data(bar.trading_date, [bar])

            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self.order_sys_id = 1
                self.trade_sys_id = 1
                self.data_handler.init(trading_date)
                self.__replay_bar(trading_date)
        elif (self.drive_bar_type == EnumBarType.minute) or (self.drive_bar_type == EnumBarType.hour):
            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self.order_sys_id = 1
                self.trade_sys_id = 1
                self.data_handler.init(trading_date)
                for instrument_id in self.subscribe_futures:
                    bar_series = self.data_handler.load_bar_series_by_date(
                        EnumMarket.期货, instrument_id, self.drive_bar_interval, self.drive_bar_type, trading_date, trading_date)
                    if instrument_id == self.drive_code:
                        self.drive_replay_data.add_data(trading_date, bar_series)
                    else:
                        self.other_replay_data_map[instrument_id].add_data(trading_date, bar_series)

                self.__replay_bar(trading_date)
        elif self.drive_bar_type == EnumBarType.tick:
            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self.order_sys_id = 1
                self.trade_sys_id = 1
                self.data_handler.init(trading_date)

                for instrument_id in self.subscribe_futures:
                    tick_series = self.data_handler.load_tick_series(EnumMarket.期货, instrument_id, trading_date)
                    if instrument_id == self.drive_code:
                        self.drive_replay_data.add_data(trading_date, tick_series)
                    else:
                        self.other_replay_data_map[instrument_id].add_data(trading_date, tick_series)

                self.__replay_tick(trading_date)
        elif self.drive_bar_type == EnumBarType.night_am_pm:
            self.on_start()
            lst_trading_days = TradingDayHelper.get_trading_days(self.start_simulate_date, self.end_simulate_date)
            for trading_date in lst_trading_days:
                self.trading_date = trading_date
                self.order_sys_id = 1
                self.trade_sys_id = 1
                self.data_handler.init(trading_date)

                for instrument_id in self.subscribe_futures:
                    bar_series = self.data_handler.load_night_am_pm_bar_series_by_date(
                        EnumMarket.期货, self.drive_code, self.drive_bar_interval, self.drive_bar_type, trading_date, trading_date)
                    if instrument_id == self.drive_code:
                        self.drive_replay_data.add_data(trading_date, bar_series)
                    else:
                        self.other_replay_data_map[instrument_id].add_data(trading_date, bar_series)

                self.__replay_bar(trading_date)

        self.generate_strategy_report()
        self.on_end()
        self.run_seconds = time.time() - t0
        print('策略运行完毕,耗时：{0}秒'.format(self.run_seconds))

    def day_begin(self, trading_date, tick_now):
        """
        交易日开始
        :param trading_date:
        :param tick_now:
        """
        self.tick_now = tick_now
        self.data_handler.trading_day = trading_date
        if self.future_data is None:
            self.future_data = FutureData()
            self.future_data.asset = FutureAsset()
            self.future_data.asset.product_code = self.product_code
            self.future_data.asset.strategy_id = self.strategy_id
            self.future_data.asset.fund_balance = self.fund_balance
            self.future_data.asset.cash = self.fund_balance
            self.future_data.asset.available_cash = self.fund_balance
            self.future_data.asset.pre_fund_balance = self.fund_balance
            self.future_data.asset.trading_date = trading_date
            self.future_data.next_asset = self.future_data.asset
        self.future_cache.day_begin(trading_date, self.future_data)
        self.indicators.clear()
        self.on_init()

    def day_end(self):
        """
        交易日结束
        """
        self.future_data = self.future_cache.day_end()
        self.all_assets.append(self.future_data.asset)
        for order in self.future_data.orders:
            self.all_orders.append(order)
            if order.direction == EnumBuySell.买入:
                direction = '买入'
            else:
                direction = '卖出'
            if order.open_close == EnumOpenClose.开仓:
                open_close = '开仓'
            else:
                open_close = '平仓'
            self.lst_order.append([order.trading_date, order.order_time, order.instrument_id, order.order_price, direction, open_close, order.order_volume,
                                   order.order_status])
        for trade in self.future_data.trades:
            self.all_trades.append(trade)
            if trade.direction == EnumBuySell.买入:
                direction = '买入'
            else:
                direction = '卖出'
            if trade.open_close == EnumOpenClose.开仓:
                open_close = '开仓'
            else:
                open_close = '平仓'
            self.lst_trade.append([trade.trading_date, trade.trade_time, trade.instrument_id, trade.trade_price, direction, open_close, trade.trade_volume])
        for position in self.future_data.positions:
            self.all_positions.append(position)
            if position.direction == EnumPositionDirection.多头:
                direction = '多头'
            else:
                direction = '空头'
            self.lst_position.append([position.trading_date, position.instrument_id, direction, position.volume, position.last_price,
                                      position.position_profit, position.market_value, position.num_holding_day])

        for position_detail in self.future_data.position_details:
            self.all_position_details.append(position_detail)
            if position_detail.direction == EnumPositionDirection.多头:
                direction = '多头'
            else:
                direction = '空头'
            if position_detail.position_type == EnumPositionType.今仓:
                position_type = '今仓'
            else:
                position_type = '昨仓'
            self.lst_position_detail.append([position_detail.trading_date, position_detail.instrument_id, direction, position_detail.volume,
                                             position_detail.open_price, position_detail.open_time, position_type,
                                             position_detail.position_profit, position_detail.float_profit, position_detail.market_value])

        self.lst_asset.append([self.future_data.asset.trading_date, self.future_data.asset.pre_fund_balance, self.future_data.asset.fund_balance,
                               self.future_data.asset.close_profit, self.future_data.asset.position_profit,
                               self.future_data.asset.close_profit + self.future_data.asset.position_profit,
                               self.future_data.asset.available_cash, self.future_data.asset.margin, self.future_data.asset.fee])

    def __replay_bar(self, trading_date):
        """
        播放bar
        :param trading_date:
        """
        self.drive_replay_data.current_trading_date = trading_date
        for replay_data in self.other_replay_data_map.values():
            replay_data.current_trading_date = trading_date

        if trading_date in self.drive_replay_data.data_block_map.keys():
            bar_series = self.drive_replay_data.data_block_map[trading_date].data_list
        else:
            bar_series = None
        try:
            tick_now = bar_series[0].begin_time + datetime.timedelta(seconds=-2)
            trading_date = bar_series[0].trading_date
            self.day_begin(trading_date, tick_now)
            for bar in bar_series:
                bar.instrument_id = self.drive_code
                self.data_handler.on_bar(bar)
                self.last_bar = bar
                self.tick_now = bar.end_time
                self.future_cache.on_bar(bar)
                self.last_bar_map[self.drive_code] = bar
                for indicator in self.indicators:
                    indicator.calculate()

                is_ready = True
                for key in self.other_replay_data_map.keys():
                    res = self.other_replay_data_map[key].replay_bar_to_time(self.tick_now)
                    if res[0]:
                        for other_bar in res[1]:
                            other_bar.instrument_id = key
                            self.data_handler.on_bar(other_bar)
                            self.future_cache.on_bar(other_bar)
                            self.last_bar_map[key] = other_bar
                    else:
                        is_ready = False
                        break
                if is_ready:
                    self.on_bar(bar)

            self.on_exit()
            self.day_end()
        except Exception as e:
            if (bar_series is None) or (len(bar_series) == 0):
                print('{0}@{1},缺失数据'.format(self.drive_code, self.trading_date))
                self.day_begin(self.trading_date, self.trading_date)
                self.on_exit()
                self.day_end()
            else:
                print(str(e))
                raise e

    def __replay_tick(self, tick_series):
        """
        播放tick
        :param tick_series:
        """
        tick_now = tick_series[0].date_time + datetime.timedelta(seconds=-2)
        trading_date = tick_series[0].trading_day
        self.day_begin(trading_date, tick_now)
        for tick in tick_series:
            tick.instrument_id = self.drive_code
            self.data_handler.on_tick(tick)
            self.last_tick = tick
            self.tick_now = tick.date_time
            self.future_cache.on_tick(tick)
            for indicator in self.indicators:
                indicator.calculate()
            self.on_tick(tick)

        self.on_exit()
        self.day_end()

    def send_order(self, instrument_id, buy_sell, open_close, volume, price, order_time=None, remark=''):
        """
        发送委托
        :param remark:
        :param order_time:
        :param instrument_id:
        :param buy_sell:
        :param open_close:
        :param volume:
        :param price:
        """
        order = FutureOrder()
        order.order_sys_id = self.order_sys_id
        order.product_code = self.product_code
        order.strategy_id = self.strategy_id
        order.account_id = instrument_id
        order.instrument_id = instrument_id
        order.direction = buy_sell
        order.open_close = open_close
        order.order_volume = volume
        order.order_price = price
        order.trading_date = self.trading_date
        if order_time is not None:
            order.order_time = order_time
        else:
            if order.instrument_id in self.last_bar_map:
                last_bar = self.last_bar_map[order.instrument_id]
                if last_bar is not None:
                    if last_bar.open == price:
                        order.order_time = self.last_bar.begin_time
                    elif last_bar.close == price:
                        order.order_time = self.last_bar.end_time
                    else:
                        order.order_time = self.tick_now
                else:
                    order.order_time = self.tick_now
            else:
                order.order_time = self.tick_now
        order.order_status = '已成交'
        self.future_cache.on_order(order)
        self.order_sys_id += 1
        self.on_order(order)

        trade = FutureTrade()
        trade.order_sys_id = order.order_sys_id
        trade.trade_sys_id = self.trade_sys_id
        trade.product_code = self.product_code
        trade.strategy_id = self.strategy_id
        trade.account_id = instrument_id
        trade.instrument_id = instrument_id
        trade.direction = buy_sell
        trade.open_close = open_close
        trade.trade_volume = volume
        trade.trade_price = price
        trade.trading_date = self.trading_date
        trade.trade_time = order.order_time
        trade.remark = remark
        self.future_cache.on_trade(trade)
        self.trade_sys_id += 1
        if self.last_bar is not None:
            print('[{0}-{1}][开:{3},收:{4}]:{2}'.format(self.last_bar.begin_time.strftime('%H:%M:%S'),
                                                      self.last_bar.end_time.strftime('%H:%M:%S'), trade.to_string(), self.last_bar.open,
                                                      self.last_bar.close))
        elif self.last_tick is not None:
            print('[{0}]:{1}'.format(self.tick_now.strftime('%H:%M:%S.%f'), trade.to_string()))
        else:
            print('{0}'.format(trade.to_string()))
        self.on_trade(trade)

    @abc.abstractmethod
    def on_start(self):
        """
        回测开始
        """
        pass

    @abc.abstractmethod
    def on_init(self):
        """
        初始化
        """
        pass

    @abc.abstractmethod
    def on_bar(self, bar):
        """
        on_bar触发
        :param bar:
        """
        pass

    @abc.abstractmethod
    def on_tick(self, tick):
        """
        on_tick触发
        :param tick:
        """
        pass

    @abc.abstractmethod
    def on_order(self, order):
        """
        委托回报
        :param order:
        """
        pass

    @abc.abstractmethod
    def on_order_canceled(self, order):
        """
        撤单成功回报
        :param order:
        """
        pass

    @abc.abstractmethod
    def on_cancel_order_failed(self, order_guid, msg):
        """
        撤单失败回报
        :param order_guid:
        :param msg:
        """
        pass

    @abc.abstractmethod
    def on_order_rejected(self, order):
        """
        委托拒绝回报
        :param order:
        """
        pass

    @abc.abstractmethod
    def on_trade(self, trade):
        """
        成交回报
        :param trade:
        """
        pass

    @abc.abstractmethod
    def on_exit(self):
        """
        当日结束
        """
        pass

    @abc.abstractmethod
    def on_end(self):
        """
        回测结束
        """
        pass

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
        return self.data_handler.get_bar_series_by_date_time(market, instrument_id, interval, bar_type, begin_time, self.tick_now)

    def get_bar_series_by_length(self, market: object, instrument_id: object, interval: object, bar_type: object, max_length: object) -> object:
        """
        根据回溯根数获取K线
        :param market:
        :param instrument_id:
        :param interval:
        :param bar_type:
        :param max_length:
        :return:
        """
        return self.data_handler.get_bar_series_by_length(market, instrument_id, interval, bar_type, max_length, self.tick_now)

    def generate_strategy_report(self):
        """
        生成策略报告
        """
        self.df_asset = pd.DataFrame(self.lst_asset, columns=['日期', '昨日结存', '动态权益', '平仓盈亏', '持仓盈亏', '净利润', '可用资金', '持仓保证金', '手续费'])
        self.df_asset['累计盈亏'] = self.df_asset[['净利润']].cumsum(axis=0)
        self.df_asset['累计收益率'] = self.df_asset['累计盈亏'] / self.fund_balance
        self.df_asset['累计收益率'] = self.df_asset['累计收益率'].apply(lambda x: format(x, '.2%'))

        self.df_order = pd.DataFrame(self.lst_order, columns=['交易日', '时间', '合约', '价格', '多空', '开平', '量', '状态'])
        self.df_trade = pd.DataFrame(self.lst_trade, columns=['交易日', '时间', '合约', '价格', '多空', '开平', '量'])
        self.df_position = pd.DataFrame(self.lst_position, columns=['交易日', '合约', '多空', '总持仓', '当前价', '持仓盈亏', '合约价值', '持有天数'])
        self.df_position_detail = pd.DataFrame(self.lst_position_detail, columns=['交易日', '合约', '多空', '总持仓', '开仓价', '开仓时间',
                                                                                  '持仓类型', '持仓盈亏', '浮动盈亏', '持仓市值'])

        self.df_trade['时间'] = self.df_trade['时间'].apply(lambda x: x.strftime('%H:%M:%S'))

        self.trading_day_num = TradingDayHelper.get_trading_day_count(self.start_simulate_date, self.end_simulate_date)
        self.total_trade_lots = self.df_trade['量'].sum() / 2
        self.volume_per_day = self.total_trade_lots / len(self.df_asset)
        self.yield_rate = StrategyToolBox.calc_total_and_annual_yield_rate(self.df_asset, self.fund_balance, 243, self.trading_day_num)
        self.total_yield_rate = self.yield_rate[0]
        self.annual_yield_rate = self.yield_rate[1]
        self.profit_per_hand = StrategyToolBox.calc_profit_per_hand(self.df_asset, self.total_trade_lots)
        self.max_retrace_rate = StrategyToolBox.calc_max_retrace_rate(self.df_asset, self.fund_balance)
        self.max_retrace = self.max_retrace_rate * self.fund_balance
        self.retrace_ratio = StrategyToolBox.calc_retrace_ratio(self.max_retrace_rate, self.annual_yield_rate)
        self.sharpe_ratio = StrategyToolBox.calc_sharpe_ratio(self.df_asset, self.fund_balance)
        self.max_daily_loss = self.df_asset['净利润'].min()
        self.continuous_innovation_high_days = StrategyToolBox.calc_max_continuous_no_innovation_high_days(self.df_asset)
        self.max_loss_days = StrategyToolBox.calc_max_loss_days(self.df_asset)
        self.lst_summary = [
            [self.drive_code, self.start_simulate_date, self.end_simulate_date, self.trading_day_num, self.total_trade_lots, self.volume_per_day,
             self.total_yield_rate, self.annual_yield_rate, self.profit_per_hand, self.max_retrace, self.max_retrace_rate, self.retrace_ratio, self.sharpe_ratio,
             self.max_daily_loss, self.continuous_innovation_high_days, self.max_loss_days]]
        self.df_summary = pd.DataFrame(self.lst_summary, columns=['品种', '开始日期', '截止日期', '交易天数', '总手数', '日均手数',
                                                                  '总收益', '年化收益', '每手盈利', '最大回撤值', '最大回撤', '收益回撤比', '夏普率',
                                                                  '单日最大亏损', '连续不创新高天数', '最大连续亏损天数'])

        lst_param = []
        for key in self.kwargs:
            if key not in ['factor_map', 'data_handle', 'mongodb_client']:
                lst_param.append([key, str(self.kwargs[key])])
        self.df_param = pd.DataFrame(lst_param, columns=['参数名', '参数值'])

    def save_strategy(self, excel_record_path, fig_record_path):
        """
        保存策略相关回测信息
        """
        try:
            dic_data = {
                'Asset': self.df_asset,
                'Order': self.df_order,
                'Trade': self.df_trade,
                'Position': self.df_position,
                'PositionDetail': self.df_position_detail,
                'Summary': self.df_summary,
                'Param': self.df_param,
            }
            FileToolBox.save_excel(excel_record_path, **dic_data)
            self.df_asset['累计收益率(%)'] = self.df_asset['累计收益率'].str.strip('%').astype(float) / 100
            FileToolBox.save_fig(fig_record_path, self.df_asset, '日期', ['累计收益率(%)'])
        except Exception as e:
            print(str(e))

    def save_mongodb(self, db_name, collection_name, account_id):
        """
        保存记录到数据库
        @param db_name:
        @param collection_name:
        @param account_id:
        """
        try:
            record = {
                'version': 1.0,
                'drive_code': self.drive_code,
                'start_simulate_date': self.start_simulate_date,
                'end_simulate_date': self.end_simulate_date,
                'account_id': account_id,
                '_asset': self.df_asset.to_dict('records'),
                'trade': self.df_trade.to_dict('records'),
                'summary': self.df_summary.to_dict('records')[0],
                'param': self.df_param.set_index(['参数名']).T.to_dict('records')[0],
                'update_time': datetime.datetime.now(),
                'run_seconds': self.run_seconds
            }
            db = self.mongodb_client[db_name]
            collection = db[collection_name]
            collection.insert_one(record)
        except Exception as e:
            print(str(e))
            print('保存数据库出错，自动转存文件格式保存......')
            excel_record_path = os.path.join(self.record_dir, '{0}.xlsx'.format(account_id))
            fig_record_path = os.path.join(self.record_dir, '{0}.png'.format(account_id))
            self.save_strategy(excel_record_path, fig_record_path)
