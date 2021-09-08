from SapphireQuant.Core.Entity import Entity


class FutureAsset(Entity):
    """
    期货资金明细
    """

    def __init__(self):
        super().__init__()
        self.cash = 0
        self.pre_fund_balance = 0
        self.fund_balance = 0
        self.available_cash = 0
        self.frozen_cash = 0
        self.market_value = 0
        self.position_profit = 0
        self.float_profit = 0
        self.close_profit = 0
        self.acc_close_profit = 0
        self.fee = 0
        self.current_margin = 0
        self.frozen_margin = 0
        self.margin = 0
        self.withdrawal = 0  # 出入金
        self.delivery_fee = 0  # 交割手续费

    def clone(self):
        """

        :return:
        """
        asset = FutureAsset()
        asset.cash = self.cash
        asset.pre_fund_balance = self.pre_fund_balance
        asset.fund_balance = self.fund_balance
        asset.available_cash = self.available_cash
        asset.frozen_cash = self.frozen_cash
        asset.market_value = self.market_value
        asset.position_profit = self.position_profit
        asset.float_profit = self.float_profit
        asset.close_profit = self.close_profit
        asset.acc_close_profit = self.acc_close_profit
        asset.fee = self.fee
        asset.current_margin = self.current_margin
        asset.frozen_margin = self.frozen_margin
        asset.margin = self.margin
        asset.withdrawal = self.withdrawal
        asset.delivery_fee = self.delivery_fee
        return asset

    def to_string(self):
        """
        string输出
        """
        return '日期:{0},昨日结存:{1},动态权益:{2},平仓盈亏:{3},持仓盈亏:{4},净利润:{5},可用资金:{6},持仓保证金:{7},手续费:{8},出入金:{9},交割手续费:{10}'.format(
            self.trading_date.strftime('%Y/%m/%d'), self.pre_fund_balance, self.fund_balance, self.close_profit, self.position_profit,
            self.close_profit + self.position_profit, self.available_cash, self.margin, self.fee, self.withdrawal, self.delivery_fee
        )
