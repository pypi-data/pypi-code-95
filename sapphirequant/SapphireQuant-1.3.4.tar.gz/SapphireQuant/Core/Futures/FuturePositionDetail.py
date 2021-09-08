from SapphireQuant.Core.Entity import Entity
from SapphireQuant.Core.Enum import EnumPositionType, EnumPositionDirection, EnumHedgeFlag


class FuturePositionDetail(Entity):
    """
    期货持仓
    """

    def __init__(self):
        super().__init__()
        self.instrument_id = ''
        self.broker_id = ''
        self.investor_id = ''
        self.instrument_name = ''
        self.direction = EnumPositionDirection.净持仓
        self.hedge_flag = EnumHedgeFlag.套保
        self.exchange_id = ''
        self.open_time = None
        self.trade_sys_id = ''
        self.open_price = 0
        self.volume = 0
        self.float_profit = 0
        self.position_profit = 0
        self.market_value = 0
        self.position_type = EnumPositionType.今仓

    def clone(self):
        position = FuturePositionDetail()
        position.product_code = self.product_code
        position.strategy_id = self.strategy_id
        position.instrument_id = self.instrument_id
        position.broker_id = self.broker_id
        position.investor_id = self.investor_id
        position.instrument_name = self.instrument_name
        position.direction = self.direction
        position.hedge_flag = self.hedge_flag
        position.exchange_id = self.exchange_id
        position.open_time = self.open_time
        position.open_price = self.open_price
        position.volume = self.volume
        position.float_profit = self.float_profit
        position.position_profit = self.position_profit
        position.market_value = self.market_value

        return position

    def to_string(self):
        """

        :return:
        """
        return '{0}:{1},成交编号:{2},手数:{3},开仓价:{4},持仓类型:{5},开仓时间:{6},持仓盈亏:{7},浮动盈亏:{8},持仓市值:{9}'.format(
            self.instrument_id, self.direction.chinese_name(), self.trade_sys_id, self.volume, self.open_price, self.position_type.chinese_name(),
            self.open_time.strftime('%Y%m%d'), self.position_profit, self.float_profit, self.market_value)
