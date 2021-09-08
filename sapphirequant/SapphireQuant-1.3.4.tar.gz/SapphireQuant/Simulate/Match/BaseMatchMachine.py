import abc

from SapphireQuant.Core.Enum import EnumOrderStatus
from SapphireQuant.Core.Enum.EnumMarket import EnumMarket

from SapphireQuant.Core.Futures import FutureTrade


class BaseMatchMachine:
    """
    基础撮合机
    """

    def __init__(self):
        self.order_map = {}
        self.match_serial = 0

    def get_can_cancel_orders(self):
        """
        获取可撤的委托单
        :return:
        """
        order_series = []
        for orders in self.order_map.values():
            for order in orders:
                if order.order_status.can_cancel():
                    order_series.append(order)

        return order_series

    def enter(self, order):
        """
        报单
        :param order:
        """
        instrument_id = order.instrument_id
        if instrument_id in self.order_map.keys():
            self.order_map[instrument_id].append(order)
        else:
            self.order_map[instrument_id] = []
            self.order_map[instrument_id].append(order)

    @abc.abstractmethod
    def cancel(self, order):
        """
        撤单
        :param order:
        :return:
        """
        msg = ''
        return False, msg

    @abc.abstractmethod
    def match_by_bar(self, bar):
        """
        撮合
        :param bar:
        :return:
        """
        lst_tuples = []
        if not self.check_bar(bar):
            return lst_tuples

        if len(self.order_map) <= 0:
            return lst_tuples

        if bar.instrument_id not in self.order_map.keys():
            return lst_tuples

        orders = self.order_map[bar.instrument_id]
        for i in range(len(orders)):
            order_item = orders[i]
            match_price = order_item.order_price
            match_volume = order_item.order_volume
            result = self.can_match_by_bar(bar, order_item)
            can_order = result[0]
            if can_order:
                match_item = FutureTrade()
                match_item.task_guid = order_item.task_guid
                # match_item.project_id
                match_item.product_code = order_item.product_code
                match_item.strategy_id = order_item.strategy_id
                match_item.local_id = order_item.local_id

                match_item.order_guid = order_item.guid
                match_item.order_sys_id = order_item.order_sys_id
                match_item.instrument_id = order_item.instrument_id
                match_item.market = EnumMarket.期货
                match_item.instrument_name = order_item.instrument_name
                match_item.exchange_id = order_item.exchange_id
                match_item.trade_volume = order_item.order_volume
                match_item.trade_price = match_price
                match_item.trade_time = bar.end_time
                match_item.direction = order_item.direction
                match_item.open_close = order_item.open_close
                match_item.hedge_flag = order_item.hedge_flag
                self.match_serial += 1
                match_item.trade_sys_id = '{0}'.format(self.match_serial)
                match_item.trading_date = order_item.trading_date

                order_item.volume_traded = match_item.trade_volume
                order_item.match_amount += match_item.trade_price * match_item.trade_volume
                if order_item.volume_traded == order_item.order_volume:
                    order_item.order_status = EnumOrderStatus.全部成交
                else:
                    order_item.order_status = EnumOrderStatus.部分成交
                if order_item.order_volume == match_volume:
                    order_item.remark = '完全成交:成交量{0},剩余{1},价格={2}元@{3}'.format(match_volume, order_item.order_volume - match_volume, match_price,
                                                                               bar.end_time.strftime('%Y/%m%d %H:%M:%S.%f'))
                else:
                    order_item.remark = '部分成交:成交量{0},剩余{1},价格={2}元@{3}'.format(match_volume, order_item.order_volume - match_volume, match_price,
                                                                               bar.end_time.strftime('%Y/%m%d %H:%M:%S.%f'))

                lst_tuples.append([order_item, match_item])
                if order_item.order_volume - order_item.volume_traded <= 0:
                    del orders[i]
                    i -= 1

        return lst_tuples

    @abc.abstractmethod
    def match_by_tick(self, tick):
        """
        撮合
        :param tick:
        :return:
        """
        lst_tuples = []
        if not self.check_tick(tick):
            return lst_tuples

        if len(self.order_map) <= 0:
            return lst_tuples

        if tick.instrument_id not in self.order_map.keys():
            return lst_tuples

        orders = self.order_map[tick.instrument_id]
        for i in range(len(orders)):
            order_item = orders[i]
            match_price = order_item.order_price
            match_volume = order_item.order_volume
            result = self.can_match_by_tick(tick, order_item)
            can_order = result[0]
            if can_order:
                match_item = FutureTrade()
                match_item.task_guid = order_item.task_guid
                # match_item.project_id
                match_item.product_code = order_item.product_code
                match_item.strategy_id = order_item.strategy_id
                match_item.local_id = order_item.local_id

                match_item.order_guid = order_item.guid
                match_item.order_sys_id = order_item.order_sys_id
                match_item.instrument_id = order_item.instrument_id
                match_item.market = EnumMarket.期货
                match_item.instrument_name = order_item.instrument_name
                match_item.exchange_id = order_item.exchange_id
                match_item.trade_volume = order_item.order_volume
                match_item.trade_price = match_price
                match_item.trade_time = tick.date_time
                match_item.direction = order_item.direction
                match_item.open_close = order_item.open_close
                match_item.hedge_flag = order_item.hedge_flag
                self.match_serial += 1
                match_item.trade_sys_id = '{0}'.format(self.match_serial)
                match_item.trading_date = order_item.trading_date

                order_item.volume_traded = match_item.trade_volume
                order_item.match_amount += match_item.trade_price * match_item.trade_volume
                if order_item.volume_traded == order_item.order_volume:
                    order_item.order_status = EnumOrderStatus.全部成交
                else:
                    order_item.order_status = EnumOrderStatus.部分成交
                if order_item.order_volume == match_volume:
                    order_item.remark = '完全成交:成交量{0},剩余{1},价格={2}元@{3}'.format(match_volume, order_item.order_volume - match_volume, match_price,
                                                                               tick.date_time.strftime('%Y/%m%d %H:%M:%S.%f'))
                else:
                    order_item.remark = '部分成交:成交量{0},剩余{1},价格={2}元@{3}'.format(match_volume, order_item.order_volume - match_volume, match_price,
                                                                               tick.date_time.strftime('%Y/%m%d %H:%M:%S.%f'))

                lst_tuples.append([order_item, match_item])
                if order_item.order_volume - order_item.volume_traded <= 0:
                    del orders[i]
                    i -= 1

        return lst_tuples

    @abc.abstractmethod
    def check_bar(self, bar):
        """
        检查
        :param bar:
        :return:
        """
        return True

    @abc.abstractmethod
    def check_tick(self, tick):
        """
        检查
        :param tick:
        :return:
        """
        return True

    @abc.abstractmethod
    def can_match_by_bar(self, bar, order):
        """
        是否可以撮合
        :param bar:
        :param order:
        :return:
        """
        match_price = None
        match_volume = None
        return False, match_price, match_volume

    @abc.abstractmethod
    def can_match_by_tick(self, tick, order):
        """
        是否可以撮合
        :param tick:
        :param order:
        :return:
        """
        match_price = None
        match_volume = None
        return False, match_price, match_volume
