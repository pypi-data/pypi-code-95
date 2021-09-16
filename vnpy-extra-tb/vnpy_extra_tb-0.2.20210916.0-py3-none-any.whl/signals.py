"""
@author  : MG
@Time    : 2021/4/15 15:55
@File    : signals.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
from typing import Optional

from vnpy.trader.constant import Interval
from vnpy.trader.object import BarData
from vnpy_extra.backtest.cta_strategy.template import TargetPosAndPriceTemplate
from vnpy_extra.utils.enhancement import CtaSignal, BarGenerator

from vnpy_extra_tb.ams import TBArrayManager


class TBCtaSignal(CtaSignal):
    def __init__(self, array_size: int, *, strict=False, **kwargs):
        super().__init__(array_size=array_size, strict=strict, **kwargs)
        self.am = TBArrayManager(size=array_size)
        # 增加 信号价格
        self.signal_price = 0
        # 开仓价格，等于pos!=0时的 self.signal_price
        self.target_open_price = 0
        # 平仓价格，等于pos==0时的 self.signal_price
        self.target_close_price = 0

    def get_signal_pos(self):
        return super().get_signal_pos(), self.signal_price

    def set_signal_pos(self, pos, price=None):
        super().set_signal_pos(pos)
        self.signal_price = self.win_bar.close_price if price is None else price
        if pos == 0:
            self.target_close_price = self.signal_price
        else:
            self.target_open_price = self.signal_price
