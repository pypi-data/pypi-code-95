#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:07
@File    : math.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import math
import random

import numpy as np
from numba import njit


def floor(x, precision=0):
    """带小数位精度控制的 floor"""
    if precision == 0:
        return math.floor(x)
    else:
        return math.floor(x * (10 ** precision)) / (10 ** precision)


def ceil(x, precision=0):
    """带小数位精度控制的 ceil"""
    if precision == 0:
        return math.ceil(x)
    else:
        return math.ceil(x * (10 ** precision)) / (10 ** precision)


@njit
def greatest_common_divisor_arr(multiply_arr: np.ndarray):
    """求多个数字之间的最大公约数"""
    arr_len = multiply_arr.shape[0] - 1
    arr = np.ones(arr_len)
    for _ in range(arr_len):
        arr[_] = greatest_common_divisor(multiply_arr[_], multiply_arr[_ + 1])

    gcd = np.min(arr)
    return gcd


@njit
def greatest_common_divisor(a: int, b: int):
    """
    欧几里得算法----辗转相除法
    :param a: 第一个数
    :param b: 第二个数
    :return: 最大公约数
    """
    # 如果最终余数为0 公约数就计算出来了
    if a < b:
        a, b = b, a

    while b != 0:
        temp = a % b
        a = b
        b = temp

    return a


@njit
def least_common_multiple(a: int, b: int):
    lcm = a * b / greatest_common_divisor(a, b)
    return lcm


@njit
def least_common_multiple_arr(arr: np.ndarray) -> int:
    """计算最小公倍数"""
    loop_count = arr.shape[0]
    lcm = arr[0]
    for _ in range(1, loop_count):
        lcm = least_common_multiple(lcm, arr[_])
    return lcm


def sample_weighted(ll, weights, k):
    """
    带权重、非重复取样
    :param ll:
    :param weights:
    :param k:
    :return:
    """
    ll_len = len(ll)
    if ll_len < k:
        raise ValueError(f"len(ll)={ll_len}<{k}")
    elif ll_len == k:
        return random.sample(ll, k)
    else:
        new_ll = list(range(len(ll)))
        new_ll_set = set(new_ll)
        new_weights = np.array(weights)
        new_k = k
        result_tot = []
        while True:
            result = random.choices(new_ll, weights=new_weights[new_ll], k=new_k)
            result_set = set(result)
            result_tot.extend(result_set)
            new_ll_set -= result_set
            new_k = k - len(result_tot)
            new_ll = list(new_ll_set)
            if new_k == 0:
                break

        result_tot.sort()
        if isinstance(ll, np.ndarray):
            ret = ll[result_tot]
        else:
            ret = [ll[_] for _ in result_tot]
        return ret


def _test_weighted_sample():
    ll = list(range(1, 30))
    result = sample_weighted(ll, weights=ll, k=15)
    print(result)
    ll = np.eye(29)
    result = sample_weighted(ll, weights=np.arange(1, 30), k=15)
    print(result)


if __name__ == "__main__":
    pass
