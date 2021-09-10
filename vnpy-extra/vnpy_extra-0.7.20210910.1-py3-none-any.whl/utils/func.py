"""
@author  : MG
@Time    : 2021/4/7 9:11
@File    : func.py
@contact : mmmaaaggg@163.com
@desc    : 用于保持一些常用函数工具
"""
import numpy as np


def is_cross(price1: np.ndarray, price2: np.ndarray, same_direction=False) -> int:
    """
    判断 price1 price2 两个价格序列是否交叉。price1 上穿 price2 返回 1；下穿返回-1，否则返回 0
    :param price1:
    :param price2:
    :param same_direction: 是否要求金叉时一定要方向相同.即:金叉时 price1 方向向上,死叉是 price1 方向向下.
    :return:
    """
    if price1[-2] < price2[-2] and price1[-1] >= price2[-1] and (not same_direction or price1[-2] < price1[-1]):
        return 1
    elif price1[-2] > price2[-2] and price1[-1] <= price2[-1] and (not same_direction or price1[-2] > price1[-1]):
        return -1
    else:
        return 0


if __name__ == "__main__":
    pass
