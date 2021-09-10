#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/8/18 10:37
@File    : exit_cta_signal.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
from itertools import chain

from vnpy.trader.object import BarData, TickData

from vnpy_extra.backtest.cta_strategy.template import get_interval_str
from vnpy_extra.utils.enhancement import CtaExitSignal


class DropLight2ExitSignal(CtaExitSignal):
    """
    吕尚的吊灯2出场策略
    建仓后，达到 N * ATR 利润后，回吐 N2 * ATR 开始止盈
    """
    short_name = 'dl2'

    def __init__(
            self, period: int, *,
            atr_win_size: int = 20, n_atr_2_profit: float = 4, n_atr_2_exit: float = 2, **kwargs):
        super().__init__(
            period, atr_win_size + 1,
            enable_on_tick_signal=True, enable_on_bar_signal=True, **kwargs)
        self.n_atr_2_profit = n_atr_2_profit
        # 达到 n_atr_2_profit 利润目标
        self.is_ok_profit = False
        self.n_atr_2_exit = n_atr_2_exit
        self.atr_win_size = atr_win_size
        # 记录 N * ATR 利润点
        self.profit_price_long, self.profit_price_short = None, None
        # 记录 N2 * ATR 止盈点
        self.exit_price_long, self.exit_price_short = None, None

    def on_window(self, bar: BarData):
        super().on_window(bar)
        if not self.am.inited:
            return
        pos = self.pos
        if pos == 0:
            self.is_ok_profit = False
            if self.exit_price_long:
                self.exit_price_long = None
            if self.exit_price_short:
                self.exit_price_short = None
            return
        close_price = bar.close_price
        # 检查是否到达 N1 * ATR 利润点
        if pos > 0:
            if not self.profit_price_long:
                atr = self.am.atr(self.atr_win_size)
                self.profit_price_long = self.entry_price + self.n_atr_2_profit * atr
                if self.profit_price_short:
                    self.profit_price_short = None

            if close_price > self.profit_price_long:
                self.is_ok_profit = True

        elif pos < 0:
            if not self.profit_price_short:
                atr = self.am.atr(self.atr_win_size)
                self.profit_price_short = self.entry_price - self.n_atr_2_profit * atr
                if self.profit_price_long:
                    self.profit_price_long = None

            if close_price < self.profit_price_short:
                self.is_ok_profit = True

        if self.is_ok_profit:
            close_price = bar.close_price
            # 检查是否达到 N2 * ATR 止盈点
            if pos > 0:
                if self.highest_after_entry:
                    atr = self.am.atr(self.atr_win_size)
                    self.exit_price_long = self.highest_after_entry - self.n_atr_2_exit * atr
                    self.set_stop_order_price(self.exit_price_long)
                    if self.exit_price_short:
                        self.exit_price_short = None

            elif pos < 0:
                if self.lowest_after_entry:
                    atr = self.am.atr(self.atr_win_size)
                    self.exit_price_short = self.lowest_after_entry + self.n_atr_2_exit * atr
                    self.set_stop_order_price(self.exit_price_short)
                    if self.exit_price_long:
                        self.exit_price_long = None

    def get_id_name(self):
        return '_'.join(chain(
            [getattr(self, 'short_name', self.__class__.__name__),
             get_interval_str(self.period, self.interval), str(self.atr_win_size), str(self.n_atr_2_profit),
             str(self.n_atr_2_exit)],
            [str(_) for key, _ in self.kwargs.items()
             if key not in ('interval', 'strict', 'vt_symbol', 'period', 'enable', 'strategy_obj')]))


if __name__ == "__main__":
    pass
