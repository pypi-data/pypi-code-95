from SapphireQuant.Core.Entity import Entity
from SapphireQuant.Core.Enum import EnumPositionDirection, EnumHedgeFlag


class FuturePosition(Entity):
    """
    期货持仓
    """

    def __init__(self):
        super().__init__()
        self.instrument_id = ''
        self.instrument_name = ''
        self.direction = EnumPositionDirection.净持仓
        self.hedge_flag = EnumHedgeFlag.套保
        self.exchange_id = ''
        self.last_price = 0
        self.volume = 0
        self.td_volume = 0
        self.yd_volume = 0
        self.td_open_trade = 0
        self.td_close_trade = 0
        self.open_cost = 0
        self.open_volume = 0
        self.close_volume = 0
        self.accumulated_close_profit = 0
        self.transaction_cost = 0
        self.close_profit = 0
        self.position_profit = 0
        self.market_value = 0
        self.num_holding_day = 0
        self.margin = 0

    def clone(self):
        position = FuturePosition()
        position.product_code = self.product_code
        position.strategy_id = self.strategy_id
        position.instrument_id = self.instrument_id
        position.instrument_name = self.instrument_name
        position.direction = self.direction
        position.hedge_flag = self.hedge_flag
        position.exchange_id = self.exchange_id
        position.last_price = self.last_price
        position.volume = self.volume
        position.td_volume = self.td_volume
        position.yd_volume = self.yd_volume
        position.td_open_trade = self.td_open_trade
        position.td_close_trade = self.td_close_trade
        position.open_cost = self.open_cost
        position.open_volume = self.open_volume
        position.close_volume = self.close_volume
        position.accumulated_close_profit = self.accumulated_close_profit
        position.transaction_cost = self.transaction_cost
        position.close_profit = self.close_profit
        position.position_profit = self.position_profit
        position.market_value = self.market_value
        position.margin = self.margin

        return position

    def to_string(self):
        """

        :return:
        """
        return '{0}:{1},总仓:{2},昨仓:{3},今仓:{4},持仓均价:{5},平仓盈亏:{6},持仓盈亏:{7},占用保证金:{8},持仓市值:{9}'.format(
            self.instrument_id, self.direction.chinese_name(), self.volume, self.yd_volume, self.td_volume, self.open_cost, self.close_profit, self.position_profit, self.margin,
            self.market_value)
