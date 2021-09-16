# -*- coding: utf-8 -*-

import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime
import os
from threading import current_thread


import pandas as pd


from idebug import *
from kiwoomde import *





class ProfitValuator(BaseClass):
    def __init__(self, buyprc, buymoney):
        self.tax_pct = '0.23%'
        self.real_commission_pct = '0.03%'
        self.test_commission_pct = '0.7%'
        self.goal_pct = '0.2%'
        # 모의투자라 하더라도, 실전 수수료율을 적용해서 해보자
        self.commission_pct = self.real_commission_pct

        self.tax_rate = parse_numStr(self.tax_pct)
        self.commission_rate = round(parse_numStr(self.commission_pct), 4)
        self.goal_rate = parse_numStr(self.goal_pct)
        self.buyprc = parse_numStr(buyprc)
        self.buymoney = parse_numStr(buymoney)

    def calc(self, curprc):
        self.curprc = parse_numStr(curprc)
        self.current_rate = (self.curprc / self.buyprc) - 1
        self.profit_rate = self.current_rate - (self.tax_rate + self.commission_rate)

        self.profit = self.buymoney * self.profit_rate

        if self.profit_rate >= self.goal_rate:
            logger.info("calc | 매도주문 고고고~")
            self.should_sell = True
            self.summary()
        else:
            self.should_sell = False

        return self

    def summary(self):
        current_pct = "{:.2%}".format(self.current_rate)
        cost_pct = "{:.2%}".format(self.tax_rate + self.commission_rate)
        profit_pct = "{:.2%}".format(self.profit_rate)
        profit = "{:,}".format(int(self.profit))
        buymoney = "{:,}".format(int(self.buymoney))
        curprc = "{:,}".format(self.curprc)

        # logger.info(self._getloc('monitor_realdata'))
        # print(f"""==================== 매도시 수익평가 ====================
        # 현재수익률 = 가격변동률 - (세율 + 수수료율)
        # {profit_pct} = {current_pct} - ({self.tax_pct} + {self.commission_pct})
        # 평가손익 = 매입금액 x 현재수익률
        # {profit} = {buymoney} x {profit_pct}
        # """)

        print(f"""==================== 매도시 수익평가 ====================
        현재수익률 = 가격변동률 - (세율 + 수수료율)
        {profit_pct} = {current_pct} - {cost_pct} [현재가: {curprc}]
        평가손익 = 매입금액 x 현재수익률
        {profit} = {buymoney} x {profit_pct}
        """)
