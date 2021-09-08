import datetime
import uuid

from SapphireQuant.Config.TradingDay.TradingDayHelper import TradingDayHelper
from SapphireQuant.Core.Enum import EnumPositionDirection, EnumOpenClose, EnumBuySell, EnumMarket, EnumHedgeFlag, EnumPositionType, EnumOrderStatus
from SapphireQuant.Core.Futures.FutureAsset import FutureAsset
from SapphireQuant.Core.Futures.FuturePosition import FuturePosition
from SapphireQuant.Core.Futures.FuturePositionDetail import FuturePositionDetail
from SapphireQuant.DataStorage.Cache.FutureData import FutureData
from SapphireQuant.DataStorage.Cache.PositionKey import PositionKey
from enum import Enum, unique
import pandas as pd


@unique
class EnumLiquidationType(Enum):
    """
    期货缓存清算方式
    """

    结算价 = 0,
    收盘价 = 1,


class FutureCache:
    """
    期货缓存
    和MQ，快期等对标，增加持仓明细的维护，平仓严格按照合约开仓的时间来进行先平老仓，后平新仓
    MQ的模式使用最新价进行清算
    快期等软件使用结算价进行清算
    """

    def __init__(self, transaction_rate, long_margin_rate, short_margin_rate, instrument_manager, data_handler, liquidation_type=EnumLiquidationType.结算价):
        self._trading_date = datetime.datetime.today()
        self._position_map = {}
        self._position_detail_map = {}
        self._order_map = {}
        self._trades = []
        self._asset = FutureAsset()
        self._liquidation_type = liquidation_type

        self._data_map = {}
        self._transaction_rate = transaction_rate
        self._long_margin_rate = long_margin_rate
        self._short_margin_rate = short_margin_rate
        self.instrument_manager = instrument_manager
        self.data_handler = data_handler

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

    def on_bar(self, bar):
        """
        on_bar维护缓存
        :param bar:
        """
        if bar.instrument_id not in self._data_map.keys():
            self._data_map[bar.instrument_id] = {}
        self._data_map[bar.instrument_id]['close'] = bar.close
        self._data_map[bar.instrument_id]['pre_close'] = bar.pre_close
        self._data_map[bar.instrument_id]['date_time'] = bar.end_time

    def on_tick(self, tick):
        """
        on_tick维护缓存
        :param tick:
        """
        if tick.instrument_id not in self._data_map.keys():
            self._data_map[tick.instrument_id] = {}
        self._data_map[tick.instrument_id]['close'] = tick.last_price
        self._data_map[tick.instrument_id]['pre_close'] = tick.pre_close_price
        self._data_map[tick.instrument_id]['date_time'] = tick.date_time

    def add_or_update_order(self, order):
        """
        添加或者更新order
        :param order:
        """
        if order.guid in self._order_map.keys():
            self._order_map[order.guid].update(order)
        else:
            self._order_map[order.guid] = order

    def add_trade(self, trade):
        """
        添加trade
        :param trade:
        """
        self._trades.append(trade)

    def calc_margin(self, position, volume_multiple):
        """
        计算保证金
        :param position:
        :param volume_multiple:
        :return:
        """
        if position.direction == EnumPositionDirection.多头:
            return position.volume * position.last_price * volume_multiple * self._long_margin_rate
        return position.volume * position.last_price * volume_multiple * self._short_margin_rate

    def on_order(self, order):
        """
        on_order触发
        :param order:
        """
        self.add_or_update_order(order)

    def on_order_canceled(self, order):
        """

        :param order:
        """
        self.add_or_update_order(order)

    def on_order_cancel_failed(self, order_guid, msg):
        """

        :param order_guid:
        :param msg:
        """
        pass

    def on_order_reject(self, order):
        """

        :param order:
        """
        self.add_or_update_order(order)

    def get_liquidation_info(self, instrument_id):
        """
        获取昨日收盘清算价格和当日收盘清算价格（pre_close & close） or (pre_settlement_price & settlement_price)
        :param instrument_id:
        :return:
        """
        last_tick = self.data_handler.load_last_tick(EnumMarket.期货, instrument_id, self._trading_date)
        if last_tick is not None:
            if self._liquidation_type == EnumLiquidationType.结算价:
                pre_liquidation_price = last_tick.pre_settlement_price
                # 当日结算价 下一日获取
                liquidation_price = self.data_handler.load_pre_settlement_price_by_tick(EnumMarket.期货, instrument_id, TradingDayHelper.get_next_trading_day(self._trading_date))
            else:
                pre_liquidation_price = last_tick.pre_close_price
                liquidation_price = last_tick.last_price
        else:
            pre_liquidation_price = 0.0
            liquidation_price = 0.0

        if pre_liquidation_price == 0.0:
            bar_series = self.data_handler.load_day_bar_series(EnumMarket.期货, instrument_id, TradingDayHelper.get_pre_trading_day(self._trading_date))
            if bar_series is not None and len(bar_series) > 0:
                print('未取到昨日清算价，根据昨日日线的收盘价来赋值结算价')
                pre_liquidation_price = bar_series[-1].close
            else:
                if instrument_id in self._data_map.keys():
                    if 'pre_close' in self._data_map[instrument_id].keys():
                        print('未取到昨日清算价，根据分钟线的昨收盘价来赋值结算价')
                        pre_liquidation_price = self._data_map[instrument_id]['pre_close']
                else:
                    print('未取到昨日清算价，用0来赋值结算价')
                    pre_liquidation_price = 0

        if liquidation_price == 0.0:
            print('未取到当日清算价，根据当日日线的收盘价来赋值结算价')
            bar_series = self.data_handler.load_day_bar_series(EnumMarket.期货, instrument_id, self._trading_date)
            if bar_series is not None and len(bar_series) > 0:
                liquidation_price = bar_series[-1].close
            else:
                if instrument_id in self._data_map.keys():
                    if 'close' in self._data_map[instrument_id].keys():
                        print('未取到昨日清算价，根据分钟线的收盘价来赋值结算价')
                        liquidation_price = self._data_map[instrument_id]['close']
                else:
                    print('未取到昨日清算价，用0来赋值结算价')
                    liquidation_price = 0
        return pre_liquidation_price, liquidation_price

    def on_trade(self, trade):
        """
        on_trade触发
        :param trade:
        :return:
        """
        future_info = self.instrument_manager[trade.instrument_id]
        multiplier = future_info.volume_multiple
        d_hand_fee = trade.trade_price * trade.trade_volume * multiplier * self._transaction_rate
        old_margin = 0

        liquidation_info = self.get_liquidation_info(trade.instrument_id)
        pre_liquidation_price = liquidation_info[0]

        # 持仓改变
        if trade.open_close == EnumOpenClose.开仓:
            if trade.direction == EnumBuySell.买入:
                position_direction = EnumPositionDirection.多头
            else:
                position_direction = EnumPositionDirection.空头
            position_key = PositionKey(trade.product_code, trade.strategy_id, trade.instrument_id, position_direction)

            # 添加position_detail
            position_detail = FuturePositionDetail()
            position_detail.product_code = trade.product_code
            position_detail.strategy_id = trade.strategy_id
            position_detail.trading_date = trade.trading_date
            position_detail.instrument_id = trade.instrument_id
            position_detail.instrument_name = trade.instrument_name
            position_detail.direction = position_direction
            position_detail.hedge_flag = EnumHedgeFlag.投机
            position_detail.exchange_id = trade.exchange_id
            position_detail.open_time = trade.trade_time
            position_detail.open_price = trade.trade_price
            position_detail.volume = trade.trade_volume
            position_detail.float_profit = 0.0
            position_detail.position_profit = 0.0
            position_detail.market_value = 0.0
            position_detail.position_type = EnumPositionType.今仓
            if position_key.to_string() in self._position_detail_map.keys():
                self._position_detail_map[position_key.to_string()].append(position_detail)
            else:
                self._position_detail_map[position_key.to_string()] = [position_detail]

            if position_key.to_string() in self._position_map.keys():
                position = self._position_map[position_key.to_string()]

                old_margin = self.calc_margin(position, multiplier)
                position.open_cost = (position.open_cost * position.volume + trade.trade_price * trade.trade_volume) / (position.volume + trade.trade_volume)
                position.td_open_trade += trade.trade_volume
                position.last_price = trade.trade_price
                position.transaction_cost += d_hand_fee
            else:
                # 添加持仓
                position = FuturePosition()
                position.product_code = trade.product_code
                position.strategy_id = trade.strategy_id
                position.trading_date = trade.trading_date
                position.exchange_id = trade.exchange_id
                position.instrument_id = trade.instrument_id
                position.instrument_name = trade.instrument_name
                position.open_cost = trade.trade_price
                position.volume = trade.trade_volume
                position.td_volume = trade.trade_volume
                position.transaction_cost = d_hand_fee
                position.direction = position_direction
                position.td_open_trade = trade.trade_volume

                self._position_map[position_key.to_string()] = position
        else:  # 平仓
            if trade.direction == EnumBuySell.买入:
                position_direction = EnumPositionDirection.空头
            else:
                position_direction = EnumPositionDirection.多头
            d_close_profit = 0

            # 反向持仓
            position_key = PositionKey(trade.product_code, trade.strategy_id, trade.instrument_id, position_direction)
            lst_position_detail = None
            position = None

            if position_key.to_string() in self._position_detail_map.keys():
                lst_position_detail = self._position_detail_map[position_key.to_string()]
                lst_position_detail.sort(key=lambda x: x.open_time)
                lst_left_position_detail = []

                sum_close_volume = 0
                volume_satisfied = False
                for position_detail in lst_position_detail:
                    if volume_satisfied:
                        lst_left_position_detail.append(position_detail)
                        continue

                    if (sum_close_volume + position_detail.volume) > trade.trade_volume:
                        close_volume = trade.trade_volume - sum_close_volume
                    else:
                        close_volume = position_detail.volume

                    sum_close_volume += position_detail.volume
                    if position_detail.position_type == EnumPositionType.昨仓:
                        if trade.direction == EnumBuySell.买入:
                            d_close_profit += close_volume * (trade.trade_price - pre_liquidation_price) * multiplier * -1  # 平仓是有盈亏的
                        else:
                            d_close_profit += close_volume * (trade.trade_price - pre_liquidation_price) * multiplier * 1  # 平仓是有盈亏的
                    elif position_detail.position_type == EnumPositionType.今仓:
                        if trade.direction == EnumBuySell.买入:
                            d_close_profit += close_volume * (trade.trade_price - position_detail.open_price) * multiplier * -1  # 平仓是有盈亏的
                        else:
                            d_close_profit += close_volume * (trade.trade_price - position_detail.open_price) * multiplier * 1  # 平仓是有盈亏的

                    if sum_close_volume == trade.trade_volume:
                        volume_satisfied = True
                    elif sum_close_volume > trade.trade_volume:
                        volume_satisfied = True
                        position_detail.volume = sum_close_volume - trade.trade_volume
                        lst_left_position_detail.append(position_detail)

                self._position_detail_map[position_key.to_string()] = lst_left_position_detail
            if lst_position_detail is None:
                return

            if position_key.to_string() in self._position_map.keys():
                position = self._position_map[position_key.to_string()]
            if position is None:
                return

            old_margin = self.calc_margin(position, multiplier)

            position.close_profit += d_close_profit
            position.td_close_trade += trade.trade_volume
            position.last_price = trade.trade_price
            position.transaction_cost += d_hand_fee

            self._asset.close_profit += d_close_profit
            self._asset.acc_close_profit += d_close_profit
            self._asset.cash += d_close_profit
            self._asset.fund_balance += d_close_profit

        if position_key.to_string() in self._position_detail_map.keys():
            lst_position_detail = self._position_detail_map[position_key.to_string()]
            volume = 0
            td_volume = 0
            yd_volume = 0
            sum_mv = 0
            for position_detail in lst_position_detail:
                volume += position_detail.volume
                if position_detail.position_type == EnumPositionType.今仓:
                    td_volume += position_detail.volume
                    sum_mv += position_detail.open_price * position_detail.volume
                elif position_detail.position_type == EnumPositionType.昨仓:
                    yd_volume += position_detail.volume
                    sum_mv += pre_liquidation_price * position_detail.volume

            position.volume = volume
            position.td_volume = td_volume
            position.yd_volume = yd_volume
            if position.volume != 0:
                position.open_cost = sum_mv / position.volume

        self._asset.cash -= d_hand_fee
        self._asset.fund_balance -= d_hand_fee
        self._asset.fee += d_hand_fee

        # 统一根据持仓价格计算保证金

        margin = self.calc_margin(position, multiplier)
        self._asset.margin += margin - old_margin
        self._asset.available_cash = self._asset.fund_balance - self._asset.margin

        self.add_trade(trade)

    def day_begin(self, trading_date, future_data):
        """
        当天开始，缓存初始化
        :param trading_date:
        :param future_data:
        """
        self._trading_date = trading_date
        self._position_map.clear()
        self._position_detail_map.clear()
        self._order_map.clear()
        self._trades.clear()
        self._asset = future_data.next_asset
        for position in future_data.next_positions:
            key = PositionKey(position.product_code, position.strategy_id, position.instrument_id, position.direction)
            self._position_map[key.to_string()] = position
        for position_detail in future_data.next_position_details:
            key = PositionKey(position_detail.product_code, position_detail.strategy_id, position_detail.instrument_id, position_detail.direction)
            if key.to_string() in self._position_detail_map.keys():
                self._position_detail_map[key.to_string()].append(position_detail)
            else:
                self._position_detail_map[key.to_string()] = [position_detail]

    def day_end(self):
        """
        当天结束，缓存清算
        :return:
        """
        next_trading_day = TradingDayHelper.get_next_trading_day(self._trading_date)
        self._asset.position_profit = 0
        d_deposit = 0
        d_market_value = 0
        position_details = []
        next_position_details = []
        for lst_position_detail in self._position_detail_map.values():
            for position_detail in lst_position_detail:
                position_details.append(position_detail)
                future_info = self.instrument_manager[position_detail.instrument_id]
                d_multiplier = future_info.volume_multiple

                liquidation_info = self.get_liquidation_info(position_detail.instrument_id)
                pre_liquidation_price = liquidation_info[0]
                liquidation_price = liquidation_info[1]

                position_detail.position_profit = 0.0
                if liquidation_price > 0:
                    position_profit = 0.0
                    if position_detail.position_type == EnumPositionType.今仓:
                        if position_detail.direction == EnumPositionDirection.多头:
                            position_profit += (liquidation_price - position_detail.open_price) * position_detail.volume * d_multiplier * 1
                        else:
                            position_profit += (liquidation_price - position_detail.open_price) * position_detail.volume * d_multiplier * -1
                    elif position_detail.position_type == EnumPositionType.昨仓:
                        if position_detail.direction == EnumPositionDirection.多头:
                            position_profit += (liquidation_price - pre_liquidation_price) * position_detail.volume * d_multiplier * 1
                        else:
                            position_profit += (liquidation_price - pre_liquidation_price) * position_detail.volume * d_multiplier * -1

                    self._asset.position_profit += position_profit
                    self._asset.fund_balance += position_profit
                    position_detail.position_profit = position_profit
                    if position_detail.direction == EnumPositionDirection.多头:
                        position_detail.market_value = liquidation_price * position_detail.volume * d_multiplier * 1
                    else:
                        position_detail.market_value = liquidation_price * position_detail.volume * d_multiplier * -1
                    d_market_value += position_detail.market_value

                if position_detail.volume > 0:
                    next_position_detail = position_detail.clone()
                    next_position_detail.guid = uuid.uuid1()
                    next_position_detail.position_type = EnumPositionType.昨仓
                    next_position_detail.trading_date = next_trading_day
                    next_position_detail.position_profit = 0
                    next_position_details.append(next_position_detail)

        next_positions = []
        for key in self._position_map.keys():
            position = self._position_map[key]
            lst_position_detail = []
            if key in self._position_detail_map.keys():
                lst_position_detail = self._position_detail_map[key]
            future_info = self.instrument_manager[position.instrument_id]
            d_multiplier = future_info.volume_multiple

            position.position_profit = 0.0

            liquidation_info = self.get_liquidation_info(position.instrument_id)
            liquidation_price = liquidation_info[1]

            position.last_price = liquidation_price
            position.market_value = 0
            for position_detail in lst_position_detail:
                position.market_value += position_detail.market_value
                position.position_profit += position_detail.position_profit

            d_deposit += self.calc_margin(position, d_multiplier)

            if position.volume > 0:
                next_position = position.clone()
                next_position.guid = uuid.uuid1()
                next_position.td_volume = 0
                next_position.yd_volume = position.volume
                next_position.close_volume = 0
                next_position.trading_date = next_trading_day
                next_position.td_close_trade = 0
                next_position.td_open_trade = 0
                next_position.close_profit = 0
                next_position.position_profit = 0
                next_position.num_holding_day = position.num_holding_day + 1
                next_positions.append(next_position)

        self._asset.margin = d_deposit
        self._asset.market_value = d_market_value
        self._asset.available_cash = self._asset.fund_balance - self._asset.margin

        next_asset = self._asset.clone()
        next_asset.guid = uuid.uuid1()
        next_asset.trading_date = next_trading_day
        next_asset.close_profit = 0
        next_asset.position_profit = 0
        next_asset.fee = 0
        next_asset.pre_fund_balance = self._asset.fund_balance

        next_future_data = FutureData()
        next_future_data.asset = self._asset
        next_future_data.positions = self._position_map.values()
        next_future_data.position_details = position_details
        next_future_data.orders = self._order_map.values()
        next_future_data.trades = []
        next_future_data.next_asset = next_asset
        next_future_data.next_positions = next_positions
        next_future_data.next_position_details = next_position_details

        for trade in self._trades:
            next_future_data.trades.append(trade)

        self._add_future_data(next_future_data)

        return next_future_data

    def on_end(self):
        """
        缓存结束，生成相应的DataFrame
        """
        self.df_asset = pd.DataFrame(self.lst_asset, columns=['产品', '策略', '日期', '昨日结存', '动态权益', '平仓盈亏', '持仓盈亏', '净利润', '可用资金', '持仓保证金', '手续费'])
        self.df_asset['累计盈亏'] = self.df_asset[['净利润']].cumsum(axis=0)
        self.df_asset['累计收益率'] = self.df_asset['累计盈亏'] / self.df_asset.iloc[0]['昨日结存']
        self.df_asset['累计收益率'] = self.df_asset['累计收益率'].apply(lambda x: format(x, '.2%'))

        self.df_order = pd.DataFrame(self.lst_order, columns=['产品', '策略', '交易日', '时间', '合约', '价格', '多空', '开平', '量', '状态'])
        self.df_trade = pd.DataFrame(self.lst_trade, columns=['产品', '策略', '交易日', '时间', '合约', '价格', '多空', '开平', '量'])
        self.df_position = pd.DataFrame(self.lst_position, columns=['产品', '策略', '交易日', '合约', '多空', '总持仓', '当前价', '持仓盈亏', '合约价值', '持有天数'])
        self.df_position_detail = pd.DataFrame(self.lst_position_detail, columns=['产品', '策略', '交易日', '合约', '多空', '总持仓', '开仓价', '开仓时间',
                                                                                  '持仓类型', '持仓盈亏', '浮动盈亏', '持仓市值'])

        self.df_trade['时间'] = self.df_trade['时间'].apply(lambda x: x.strftime('%H:%M:%S'))

    def _add_future_data(self, future_data):
        """
        新增期货清算数据
        :param future_data:
        """
        self.all_assets.append(future_data.asset)
        self.lst_asset.append([future_data.asset.product_code, future_data.asset.strategy_id,
                               future_data.asset.trading_date, future_data.asset.pre_fund_balance, future_data.asset.fund_balance,
                               future_data.asset.close_profit, future_data.asset.position_profit,
                               future_data.asset.close_profit + future_data.asset.position_profit,
                               future_data.asset.available_cash, future_data.asset.margin, future_data.asset.fee])

        for order in future_data.orders:
            self.all_orders.append(order)
            self.lst_order.append(
                [order.product_code, order.strategy_id, order.trading_date, order.order_time, order.instrument_id, order.order_price,
                 order.direction.chinese_name(), order.open_close.chinese_name(), order.order_volume,
                 order.order_status])

        for trade in future_data.trades:
            self.all_trades.append(trade)
            self.lst_trade.append(
                [trade.product_code, trade.strategy_id, trade.trading_date, trade.trade_time, trade.instrument_id, trade.trade_price,
                 trade.direction.chinese_name(), trade.open_close.chinese_name(), trade.trade_volume])

        for position in future_data.positions:
            self.all_positions.append(position)
            self.lst_position.append([position.product_code, position.strategy_id, position.trading_date, position.instrument_id,
                                      position.direction.chinese_name(), position.volume, position.last_price,
                                      position.position_profit, position.market_value, position.num_holding_day])

        for position_detail in future_data.position_details:
            self.all_position_details.append(position_detail)
            self.lst_position_detail.append([position_detail.product_code, position_detail.strategy_id,
                                             position_detail.trading_date, position_detail.instrument_id,
                                             position_detail.direction.chinese_name(), position_detail.volume,
                                             position_detail.open_price, position_detail.open_time, position_detail.position_type.chinese_name(),
                                             position_detail.position_profit, position_detail.float_profit, position_detail.market_value])

    def get_position(self, product_code, strategy_id, instrument_id, direction):
        """
        获取缓存持仓
        :param product_code:
        :param strategy_id:
        :param instrument_id:
        :param direction:
        :return:
        """
        key = PositionKey(product_code, strategy_id, instrument_id, direction)
        key = key.to_string()
        if key in self._position_map.keys():
            return self._position_map[key]
        else:
            # 添加持仓
            position = FuturePosition()
            position.product_code = product_code
            position.strategy_id = strategy_id
            # position.ProjectId = trade.ProjectId
            position.trading_date = self._trading_date
            position.exchange_id = ''
            position.instrument_id = instrument_id
            position.instrument_name = ''
            position.open_cost = 0
            position.volume = 0
            position.td_volume = 0
            position.transaction_cost = 0
            position.direction = direction
            position.td_open_trade = 0

            self._position_map[key] = position
            return position

    def get_future_asset(self):
        """
        获取期货资金明细
        :return:
        """
        return self._asset

    def get_future_trades(self):
        """
        获取期货成交
        :return:
        """
        return self._trades

    def get_future_orders(self):
        """
        获取期货委托
        :return:
        """
        return list(self._order_map.values())

    def get_can_cancel_orders(self):
        """
        获取可撤委托
        :return:
        """
        order_series = []
        for order in self._order_map.values():
            if order.order_status != EnumOrderStatus.全部成交 and order.order_status != EnumOrderStatus.已撤:
                order_series.append(order)

        return order_series

    def get_future_positions(self):
        """
        获取期货持仓
        :return:
        """
        position_series = list(self._position_map.values())
        return position_series

    def get_future_order(self, guid):
        """
        获取期货委托
        :param guid:
        :return:
        """
        if guid in self._order_map.keys():
            return self._order_map[guid]
        return None
