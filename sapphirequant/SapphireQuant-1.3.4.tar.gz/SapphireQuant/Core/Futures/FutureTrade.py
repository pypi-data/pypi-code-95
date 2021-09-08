import datetime
import uuid

from SapphireQuant.Core.Entity import Entity
from SapphireQuant.Core.Enum import EnumMarket, EnumBuySell, EnumOpenClose, EnumHedgeFlag


class FutureTrade(Entity):
    """
    期货成交
    """
    def __init__(self):
        super().__init__()
        self.task_guid = uuid.uuid1()
        self.local_id = ''
        self.broker_id = ''
        self.investor_id = ''
        self.user_id = ''
        self.order_guid = ''
        self.order_sys_id = ''
        self.trade_sys_id = ''
        self.instrument_id = ''
        self.instrument_name = ''
        self.market = EnumMarket.期货
        self.exchange_id = ''
        self.direction = EnumBuySell.买入
        self.open_close = EnumOpenClose.开仓
        self.hedge_flag = EnumHedgeFlag.套保
        self.trade_volume = 0
        self.trade_price = 0
        self.trade_amount = 0
        self.trade_time = datetime.datetime.today()
        self.remark = ''

    def to_string(self):
        """

        :return:
        """
        return '期货成交:{0}{1}{2}手[{3}]成交价{4}@{5},{6}'.format(
            self.direction.chinese_name(), self.open_close.chinese_name(), self.trade_volume, self.instrument_id, self.trade_price, self.trade_time.strftime('%H:%M:%S.%f'), self.remark)
