"""
@author  : MG
@Time    : 2021/4/15 15:57
@File    : ams.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""

import numpy as np
from vnpy_extra.utils.enhancement import ArrayManager


class TBArrayManager(ArrayManager):
    """
    该模块是将TB内置的函数、算法转编译为VNPY，以达到python编写策略TB化，从而降低使用和学习成本
    """

    def adaptive_move_avg(self, price=None, EffRatioLength=10, FastAvgLength=2, SlowAvgLength=30,
                          array: bool = False):
        """
        :param price: 价格序列，默认为None，使用 self.base_price 也就是收盘价作为计算基准
        :param EffRatioLength:自适应周期数，也是计算er效率系数的参数
        :param FastAvgLength:短周期数
        :param SlowAvgLength:长周期数
        :param array: 是否返回数组
        :return: 卡夫曼自适应均线
        """
        if price is None:
            price = self.base_price

        ama_value = []
        fastest = 2 / (FastAvgLength + 1)
        slowest = 2 / (SlowAvgLength + 1)
        direction = (abs(price[-1] - price[-EffRatioLength]))

        if self.count > EffRatioLength:
            for i in range(1, period):
                move = abs(self.close_array[-i] - self.close_array[-1 - i])
                volSum += move
            if volSum == 0:
                er = 0
            else:
                er = direction[-1] / volSum

            cc = er * (fastest - slowest) + slowest
            sc = cc ** 2

        if self.count > 2:
            ama_value.append(self.close_array[-1] + sc * (self.close_array[-1] - self.close_array[-2]))
        else:
            # self.write_log(self.ret)
            ama_value.append(ama_value[-1] + sc * (self.close_array[-1] - ama_value[-1]))

        if array:
            return ama_value

        return ama_value[-1]

    def avg_true_range(self, length=14, array: bool = False):
        """
        :param length: TrueRange真实波动周期
        :param array:  是否返回数组
        :return: 真实平均波幅
        """
        TureRange = [0]
        atr = []
        TureRange.append(max(
            max((self.high_array[-1] - self.low_array[-1]), abs(self.close_array[-2] - self.high_array[-1])),
            abs(self.close_array[-2] - self.low_array[-1])
        ))
        atr.append(np.mean(TureRange[-length:]))
        if array:
            return atr

        return atr[-1]

    def average(self, price=None, length=20, array: bool = False):
        """
        :param price: 价格序列，默认为None，使用 self.base_price 也就是收盘价作为计算基准
        :param length: 平均线周期
        :param array: 是否返回数组
        :return: 简单平均线
        """
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def w_average(self, price=None, length=20, array: bool = False):
        """
        :param price:价格序列，默认为None，使用 self.base_price 也就是收盘价作为计算基准
        :param length:加权平均线周期
        :param array: 是否返回数组
        :return: 加权移动平均
        """
        w_average = [0]
        for i in range(length):
            WtdSum += (length - i) * price[-i]
        CumWt = (length + 1) * length * 0.5

        w_average.append(WtdSum / CumWt)
        if array:
            return w_average
        return w_average[-1]

