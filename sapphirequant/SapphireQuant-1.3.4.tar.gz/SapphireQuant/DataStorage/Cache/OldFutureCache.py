import datetime
import uuid

from SapphireQuant.Config.TradingDay import TradingDayHelper

from SapphireQuant.Core.Enum import EnumOpenClose, EnumBuySell, EnumPositionDirection, EnumMarket, EnumOrderStatus
from SapphireQuant.Core.Futures import FutureAsset, FuturePosition
from SapphireQuant.DataStorage.Cache import PositionKey, FutureData


class OldFutureCache:
    """
    期货缓存，老版本的期货缓存管理，已经弃用，不带持仓明细，清算不准确
    """
    def __init__(self, transaction_rate, long_margin_rate, short_margin_rate, instrument_manager, data_handler):
        self._trading_date = datetime.datetime.today()
        self._position_map = {}
        self._order_map = {}
        self._trades = []
        self._asset = FutureAsset()

        self._data_map = {}
        self._transaction_rate = transaction_rate
        self._longMargin_rate = long_margin_rate
        self._shortMargin_rate = short_margin_rate
        self.instrument_manager = instrument_manager
        self.data_handler = data_handler

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
            return position.volume * position.last_price * volume_multiple * self._longMargin_rate
        return position.volume * position.last_price * volume_multiple * self._shortMargin_rate

    def on_order(self, order):
        """
        on_order触发
        :param order:
        """
        self.add_or_update_order(order)

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
        # 持仓改变
        if trade.open_close == EnumOpenClose.开仓:
            if trade.direction == EnumBuySell.买入:
                position_direction = EnumPositionDirection.多头
            else:
                position_direction = EnumPositionDirection.空头
            key = PositionKey(trade.product_code, trade.strategy_id, trade.instrument_id, position_direction)
            if key.to_string() in self._position_map.keys():
                position = self._position_map[key.to_string()]

                old_margin = self.calc_margin(position, multiplier)
                position.open_cost = (position.open_cost * position.volume + trade.trade_price * trade.trade_volume) / (position.volume + trade.trade_volume)
                position.volume += trade.trade_volume
                position.td_volume += trade.trade_volume
                position.td_open_trade += trade.trade_volume
                position.last_price = trade.trade_price
                position.transaction_cost += d_hand_fee
            else:

                # 添加持仓
                position = FuturePosition()
                position.product_code = trade.product_code
                position.strategy_id = trade.strategy_id
                # position.ProjectId = trade.ProjectId
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

                self._position_map[key.to_string()] = position
        else:  # 平仓
            if trade.direction == EnumBuySell.买入:
                position_direction = EnumPositionDirection.空头
            else:
                position_direction = EnumPositionDirection.多头

            # // 反向持仓
            key = PositionKey(trade.product_code, trade.strategy_id, trade.instrument_id, position_direction)
            position = None
            if key.to_string() in self._position_map.keys():
                position = self._position_map[key.to_string()]
            if position is None:
                return

            old_margin = self.calc_margin(position, multiplier)

            pre_close = self.data_handler.load_pre_close_by_tick(EnumMarket.期货, position.instrument_id, self._trading_date)

            d_close_profit = 0
            position.volume -= trade.trade_volume
            if trade.trade_volume >= position.yd_volume:
                close_yd_volume = position.yd_volume
            else:
                close_yd_volume = trade.trade_volume

            close_td_volume = trade.trade_volume - close_yd_volume
            # 平今仓
            if trade.direction == EnumBuySell.买入:
                d_close_profit += close_td_volume * (trade.trade_price - position.open_cost) * multiplier * -1  # 平仓是有盈亏的
            else:
                d_close_profit += close_td_volume * (trade.trade_price - position.open_cost) * multiplier * 1  # 平仓是有盈亏的
            position.td_volume -= close_td_volume
            # 平老仓
            if trade.direction == EnumBuySell.买入:
                d_close_profit += close_yd_volume * (trade.trade_price - pre_close) * multiplier * -1  # 平仓是有盈亏的
            else:
                d_close_profit += close_yd_volume * (trade.trade_price - pre_close) * multiplier * 1  # 平仓是有盈亏的
            position.yd_volume -= close_yd_volume

            position.close_profit += d_close_profit
            position.td_close_trade += trade.trade_volume
            position.last_price = trade.trade_price
            position.transaction_cost += d_hand_fee

            self._asset.close_profit += d_close_profit
            self._asset.acc_close_profit += d_close_profit
            self._asset.cash += d_close_profit
            self._asset.fund_balance += d_close_profit

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
        self._order_map.clear()
        self._trades.clear()
        self._asset = future_data.next_asset
        for position in future_data.next_positions:
            key = PositionKey(position.product_code, position.strategy_id, position.instrument_id, position.direction)
            self._position_map[key.to_string()] = position

    def day_end(self):
        """
        当天结束，缓存清算
        :return:
        """
        next_trading_day = TradingDayHelper.get_next_trading_day(self._trading_date)
        self._asset.position_profit = 0
        d_deposit = 0
        d_market_value = 0
        next_positions = []
        for position in self._position_map.values():
            future_info = self.instrument_manager[position.instrument_id]
            d_multiplier = future_info.volume_multiple

            if position.instrument_id in self._data_map.keys():
                close = self._data_map[position.instrument_id]['close']
                pre_close = self._data_map[position.instrument_id]['pre_close']
            else:
                close = self.data_handler.load_day_bar_series(EnumMarket.期货, position.instrument_id, self._trading_date)[-1].close
                pre_close = self.data_handler.load_pre_close_by_tick(EnumMarket.期货, position.instrument_id, self._trading_date)

            position.position_profit = 0.0
            position.last_price = 0
            if close > 0:
                position_profit = 0.0
                # 今仓 持仓盈亏计算
                if position.direction == EnumPositionDirection.多头:
                    position_profit += (close - position.open_cost) * position.td_volume * d_multiplier * 1
                else:
                    position_profit += (close - position.open_cost) * position.td_volume * d_multiplier * -1

                # 历史 持仓盈亏计算
                if position.direction == EnumPositionDirection.多头:
                    position_profit += (close - pre_close) * position.yd_volume * d_multiplier * 1
                else:
                    position_profit += (close - pre_close) * position.yd_volume * d_multiplier * -1

                self._asset.position_profit += position_profit
                self._asset.fund_balance += position_profit
                position.last_price = close
                position.position_profit = position_profit
                if position.direction == EnumPositionDirection.多头:
                    position.market_value = close * position.volume * d_multiplier * 1
                else:
                    position.market_value = close * position.volume * d_multiplier * -1
                d_market_value += position.market_value

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
        next_future_data.orders = self._order_map.values()
        next_future_data.trades = []
        next_future_data.next_asset = next_asset
        next_future_data.next_positions = next_positions

        for trade in self._trades:
            next_future_data.trades.append(trade)

        return next_future_data

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
