import datetime
import uuid

from SapphireQuant.Core.Enum.EnumOrderSubmitStatus import EnumOrderSubmitStatus

from SapphireQuant.Core.Enum.EnumOrderStatus import EnumOrderStatus

from SapphireQuant.Core.Entity import Entity
from SapphireQuant.Core.Enum import EnumBuySell, EnumMarket, EnumOpenClose, EnumHedgeFlag


class FutureOrder(Entity):
    """
    期货委托
    """

    def __init__(self):
        super().__init__()
        self.task_guid = uuid.uuid1()
        self.local_id = ''
        self.broker_id = ''
        self.investor_id = ''
        self.user_id = ''
        self.order_sys_id = ''
        self.instrument_id = ''
        self.instrument_name = ''
        self.instrument_type = EnumMarket.期货
        self.exchange_id = ''
        self.direction = EnumBuySell.买入
        self.open_close = EnumOpenClose.开仓
        self.hedge_flag = EnumHedgeFlag.投机
        self.order_status = EnumOrderStatus.未知
        self.order_submit_status = EnumOrderSubmitStatus.un_known
        self.price_type = 0
        self.order_price = 0.0
        self.order_volume = 0
        self.order_time = datetime.datetime.today()
        self.volume_traded = 0
        self.volume_left = self.order_volume - self.volume_traded
        self.volume_canceled = 0
        self.cancel_time = datetime.datetime.today()
        self.order_reject_reason = 0
        self.match_price = 0
        self.match_amount = 0
        self.frozen_amount = 0
        self.transaction_cost = 0
        self.order_type = 0
        self.local_order_time = datetime.datetime.today()
        self.status_msg = ''
        self.remark = ''
        self.is_completed = True

    def update(self, order):
        """
        更新
        :param order:
        """
        if self.is_new(order):
            self.order_sys_id = order.order_sys_id
            self.order_status = order.order_status
            self.order_price = order.order_price
            self.volume_traded = order.volume_traded
            self.match_amount = order.match_amount
            self.order_time = order.order_time
            self.local_order_time = order.local_order_time
            self.cancel_time = order.cancel_time
            self.remark = order.remark
            self.order_reject_reason = order.order_reject_reason

    def is_new(self, new_order):
        """

        :param new_order:
        :return:
        """
        if self.volume_traded <= new_order.volume_traded:
            return True

        if self.volume_traded > new_order.volume_traded:
            return False

        if self.is_completed:
            return False

        return True

    def to_string(self):
        """

        :return:
        """
        return '{0},状态[{1}],'.format(str(self.guid), self.order_status.chinese_name()) + '委托序号:{0},委托时间:{1},'.format(
            self.order_sys_id, self.order_time.strftime('%Y/%m/%d %H:%M:%S')) + '{0}@{1},[{2}][{3}]'.format(
            self.instrument_type.name, self.exchange_id, self.product_code, self.strategy_id) + '{0}{1}{2}{3}手[{4}]'.format(
            self.hedge_flag.chinese_name(), self.direction.chinese_name(), self.open_close.chinese_name(), self.order_volume, self.instrument_id) + '{0},剩:{1},'.format(
            self.order_price, self.order_volume - self.volume_traded) + '成交量:{0},成交金额:{1},撤:{2},'.format(
            self.volume_traded, self.match_amount, self.volume_canceled) + '{0},{1}'.format(self.order_reject_reason, self.status_msg)
