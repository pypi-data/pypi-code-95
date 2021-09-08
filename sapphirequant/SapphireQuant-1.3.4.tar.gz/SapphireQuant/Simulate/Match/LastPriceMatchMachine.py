from abc import ABC

from SapphireQuant.Core.Enum import EnumBuySell
from SapphireQuant.Simulate.Match.BaseMatchMachine import BaseMatchMachine


class LastPriceMatchMachine(BaseMatchMachine, ABC):
    """
    最新价撮合机
    """
    def __init__(self):
        super().__init__()

    def cancel(self, order):
        """
        撤单
        :param order:
        :return:
        """
        if order.instrument_id in self.order_map.keys():
            orders = self.order_map[order.instrument_id]
            for i in range(len(orders)):
                data = orders[i]
                if data.local_id == order.loacl_id or data.order_sys_id == order.order_sys_id:
                    order = data
                    del orders[i]
                    break
            msg = '撤单成功'
            return True, order, msg

        msg = '未找到委托编号为{0}的订单'.format(order.order_sys_id)
        return False, order, msg

    def can_match_by_bar(self, bar, order):
        """

        :param bar:
        :param order:
        :return:
        """
        if order.direction == EnumBuySell.买入:
            if order.order_price >= bar.close:
                match_price = bar.close
                match_volume = order.order_volume
                return True, match_price, match_volume

        elif order.direction == EnumBuySell.卖出:
            if order.order_price <= bar.close:
                match_price = bar.close
                match_volume = order.order_volume
                return True, match_price, match_volume

        return False, None, None

    def can_match_by_tick(self, tick, order):
        """

        :param tick:
        :param order:
        :return:
        """
        if order.direction == EnumBuySell.买入:
            if order.order_price > tick.bid_price1:
                match_price = min(order.order_price, tick.last_price)
                match_volume = order.order_volume
                return True, match_price, match_volume

        elif order.direction == EnumBuySell.卖出:
            if order.order_price < tick.ask_price1:
                match_price = max(order.order_price, tick.last_price)
                match_volume = order.order_volume
                return True, match_price, match_volume

        return False, None, None