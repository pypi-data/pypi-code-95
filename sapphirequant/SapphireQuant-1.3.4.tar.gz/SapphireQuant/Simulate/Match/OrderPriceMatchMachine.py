from abc import ABC

from SapphireQuant.Core.Futures import FutureTrade

from SapphireQuant.Core.Enum import EnumBuySell, EnumMarket, EnumOrderStatus
from SapphireQuant.Simulate.Match.BaseMatchMachine import BaseMatchMachine


class OrderPriceMatchMachine(BaseMatchMachine, ABC):
    """
    委托价撮合机
    委托必成
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
                match_item.trade_time = order_item.order_time
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

    def can_match_by_bar(self, bar, order):
        """

        :param bar:
        :param order:
        :return:
        """
        return True, order.order_price, order.order_volume

    def can_match_by_tick(self, tick, order):
        """

        :param tick:
        :param order:
        :return:
        """
        return True, order.order_price, order.order_volume
