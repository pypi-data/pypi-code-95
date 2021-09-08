from SapphireQuant.Core.Enum import EnumSimulateMatchMode, EnumOrderStatus, EnumOpenClose, EnumBuySell, EnumPositionDirection, EnumTradeEventType
from SapphireQuant.Simulate.Match.LastPriceMatchMachine import LastPriceMatchMachine
from SapphireQuant.Simulate.Match.OrderPriceMatchMachine import OrderPriceMatchMachine


class MatchCenter:
    """
    撮合机
    """

    def __init__(self, future_cache, match_mode, long_margin_rate, short_margin_rate):
        self.on_trade_event = []
        self.on_order_event = []
        self.on_order_reject_event = []
        self.on_order_canceled_event = []
        self.on_order_cancel_failed_event = []

        self._future_cache = future_cache
        self._long_margin_rate = long_margin_rate
        self._short_margin_rate = short_margin_rate
        self._machine = None
        self._trading_date = None
        self._current_time = None
        self._order_serial = 0
        self._order_ref = 0
        if match_mode == EnumSimulateMatchMode.last_price:
            self._machine = LastPriceMatchMachine()
        else:
            self._machine = OrderPriceMatchMachine()

    def get_can_cancel_orders(self):
        """
        获取可撤单列表
        """
        self._machine.get_can_cancel_orders()

    def on_tick(self, tick):
        """

        :param tick:
        """
        self._trading_date = tick.trading_date
        self._current_time = tick.date_time

    def on_bar(self, bar):
        """

        :param bar:
        """
        self._trading_date = bar.trading_date
        self._current_time = bar.end_time

    def match_by_bar(self, bar):
        """

        :param bar:
        """
        self._trading_date = bar.trading_date
        self._current_time = bar.end_time
        lst_res = self._machine.match_by_bar(bar)
        for data in lst_res:
            self._on_order(data[0])
            self._on_trade(data[1])

    def match_by_tick(self, tick):
        """

        :param tick:
        """
        self._trading_date = tick.trading_date
        self._current_time = tick.date_time
        lst_res = self._machine.match_by_tick(tick)
        for data in lst_res:
            self._on_order(data[0])
            self._on_trade(data[1])

    def enter(self, order):
        """
        报单
        :param order:
        """
        self._order_serial += 1
        order.order_sys_id = '{0}'.format(self._order_serial)
        order.trading_date = self._trading_date
        if order.order_time is None:
            order.order_time = self._current_time
        if order.local_order_time is None:
            order.local_order_time = self._current_time
        order.order_status = EnumOrderStatus.未报
        self._on_order(order)
        if self._pre_check(order):
            self._machine.enter(order)
            order.order_status = EnumOrderStatus.已报
            self._on_order(order)

    def cancel_order(self, order):
        """
        撤单
        :param order:
        :return:
        """
        result = self._machine.cancel(order)
        success = result[0]
        order = result[1]
        msg = result[2]
        if success:
            order.volume_canceled = order.order_volume - order.volume_traded
            order.order_status = EnumOrderStatus.已撤
            order.trading_date = self._trading_date
            if order.cancel_time is None:
                order.cancel_time = self._current_time
            self._on_order_canceled(order)
            return True

        order.order_status = EnumOrderStatus.全部成交
        self._on_order_cancel_failed(order.OrderSysId, msg)
        return False

    def _pre_check(self, order):
        if order.open_close == EnumOpenClose.开仓:
            asset = self._future_cache.get_future_asset()
            if order.direction == EnumBuySell.买入:
                margin_rate = self._long_margin_rate
            else:
                margin_rate = self._short_margin_rate

            need_cash = order.order_price * order.order_volume * self._future_cache.instrument_manager[order.instrument_id].volume_multiple * margin_rate
            if asset.available_cash < need_cash:
                order.remark = '综合交易平台：资金不足'
                order.order_status = EnumOrderStatus.废单
                self._on_order_rejected(order)
                return False
        else:
            # 平仓要看反向持仓
            if order.direction == EnumBuySell.买入:
                position_direction = EnumPositionDirection.空头
            else:
                position_direction = EnumPositionDirection.多头

            pos = self._future_cache.get_position(order.product_code, order.strategy_id, order.instrument_id, position_direction)
            if pos is None:
                open_close = order.open_close.chiese_name()
                order.remark = '综合交易平台：{0}仓位不足'.format(open_close)
                self._on_order_rejected(order)
                return False
        return True

    def _on_trade(self, trade):
        for event in self.on_trade_event:
            print(trade.to_string())
            event(trade)

    def _on_order(self, order):
        for event in self.on_order_event:
            # if order.order_status == EnumOrderStatus.全部成交:
            #     print(order.to_string())
            event(order)

    def _on_order_rejected(self, order):
        for event in self.on_order_reject_event:
            event(order)

    def _on_order_canceled(self, order):
        for event in self.on_order_canceled_event:
            event(order)

    def _on_order_cancel_failed(self, order_sys_id, msg):
        for event in self.on_order_cancel_failed_event:
            event(order_sys_id, msg)

    def register_event(self, function, event_type):
        """
        注册事件
        :param function:
        :param event_type:
        """
        if event_type == EnumTradeEventType.on_order:
            self.on_order_event.append(function)
        elif event_type == EnumTradeEventType.on_trade:
            self.on_trade_event.append(function)
        elif event_type == EnumTradeEventType.on_order_reject:
            self.on_order_reject_event.append(function)
        elif event_type == EnumTradeEventType.on_order_cancel_failed:
            self.on_order_cancel_failed_event.append(function)
        elif event_type == EnumTradeEventType.on_order_canceled:
            self.on_order_canceled_event.append(function)

    def send_future_order(self, logic_account_name, order):
        """
        发送委托
        :param logic_account_name:
        :param order:
        :return:
        """
        self._order_ref += 1
        order.local_id = str(self._order_ref)
        self.enter(order)
        return order

    def get_future_asset(self):
        """

        :return:
        """
        return self._future_cache.get_future_asset()

    def get_future_orders(self):
        """

        :return:
        """
        return self._future_cache.get_future_orders()

    def get_future_trades(self):
        """

        :return:
        """
        return self._future_cache.get_future_trades()

    def get_future_positions(self):
        """

        :return:
        """
        return self._future_cache.get_future_positions()

    def get_future_position_details(self):
        """

        :return:
        """
        return self._future_cache.get_future_position_details()

    def get_all_future_assets(self):
        """
        获取所有的期货的账户明细
        :return:
        """
        return self._future_cache.df_asset

    def get_all_future_orders(self):
        """
        获取所有的期货委托
        :return:
        """
        return self._future_cache.df_order

    def get_all_future_trades(self):
        """
        获取所有的期货成交
        :return:
        """
        return self._future_cache.df_trade

    def get_all_future_positions(self):
        """
        获取所有的期货持仓
        :return:
        """
        return self._future_cache.df_position

    def get_all_future_position_details(self):
        """
        获取所有的持仓明细
        :return:
        """
        return self._future_cache.df_position_detail
