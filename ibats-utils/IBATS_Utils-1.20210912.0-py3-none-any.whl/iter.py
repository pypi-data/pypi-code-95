#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:11
@File    : iter.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import functools
import logging
from datetime import date, timedelta
from functools import reduce
from io import StringIO
from typing import Iterator

import numpy as np
from numba import njit

logger = logging.getLogger(__name__)


def active_coroutine(func):
    """装饰器：向前执行第一个 yield 表达式，预激活 func"""

    @functools.wraps(func)
    def primer(*arg, **kwargs):
        gen = func(*arg, **kwargs)
        next(gen)
        return gen

    return primer


def range_date(start: date, end: date, step=1):
    if start > end:
        return
    ret_date = start
    while ret_date <= end:
        yield ret_date
        ret_date += timedelta(days=step)

    if ret_date > end:
        yield end


def csv_split_chunk(file_name, csv_split_chunk_size=1024 * 1024 * 8) -> Iterator[StringIO]:
    """按照尺寸将csv文件切割成为N组字符流"""
    with open(file_name) as f:
        first_line = f.readline()
        line = f.readline()
        stream = None
        while line != "":
            # 初始化 steam
            if stream is None:
                stream = StringIO()
                stream.writelines([first_line, line])
                cur_size = len(first_line) + len(line)
            else:
                # 填充数据到 steam
                stream.write(line)

            cur_size += len(line)
            if cur_size >= csv_split_chunk_size:
                # 返回 steam
                stream.seek(0)
                yield stream
                stream = None

            line = f.readline()

        if stream is not None:
            stream.seek(0)
            yield stream


def split_chunk(l: list, n: int):
    """
    将数组按照给定长度进行分割
    :param l:
    :param n:
    :return:
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def iter_2_range(iterator, has_left_outer=True, has_right_outer=True):
    """
    将一个 N 长度的 iterator 生成 N + 1 个区间
    例如：[1,2,3] --> [[None, 1], [1, 2] [2, 3] [3, None]]
    :param iterator:
    :param has_left_outer:
    :param has_right_outer:
    :return:
    """
    last_val = None
    for val in iterator:
        if last_val is not None or has_left_outer:
            yield last_val, val
        last_val = val
    else:
        if last_val is not None and has_right_outer:
            yield last_val, None


def zip_split(*args, sep=','):
    """
    将多个字符串，按照 sep 分割对齐，形成元祖数组
    :param args: [str1, str2, ...]
    :param sep: 默认 ,
    :return:
    """
    return list(zip(*[arg.split(sep=sep) for arg in args]))


def unzip_join(tuple_list, sep=','):
    return (sep.join(arg) for arg in zip(*tuple_list))


def get_first(iterable, func, ret_func=None):
    for val in iterable:
        if func(val):
            return val if ret_func is None else ret_func(val)
    return None


def get_first_idx(iterable, func):
    for idx, n in enumerate(iterable):
        if func(n):
            return idx
    return None


@njit
def get_first_idx_larger_than(arr: np.ndarray, k):
    for i in range(len(arr)):
        if arr[i] > k:
            return i
    return -1


@njit
def get_first_idx_smaller_than(arr: np.ndarray, k):
    for i in range(len(arr)):
        if arr[i] < k:
            return i
    return -1


def get_last(iterable, comp_func, ret_func=None):
    count = len(iterable)
    for n in range(count - 1, -1, -1):
        val = iterable[n]
        if comp_func(val):
            return val if ret_func is None else ret_func(val)
    return None


def get_last_idx(iterable, func):
    """
    获取最后一个符合条件数据的数组索引
    :param iterable:
    :param func:
    :return:
    """
    count = len(iterable)
    for n in range(count - 1, -1, -1):
        if func(iterable[n]):
            return n
    return None


@njit
def get_last_idx_larger_than(arr: np.ndarray, k):
    for i in range(len(arr) - 1, -1, -1):
        if arr[i] > k:
            return i
    return -1


@njit
def get_last_idx_smaller_than(arr: np.ndarray, k):
    for i in range(len(arr) - 1, -1, -1):
        if arr[i] < k:
            return i
    return -1


@njit
def get_nth_index(arr: np.ndarray, func, count):
    c = 0
    for i in range(len(arr)):
        if func(arr[i]):
            c += 1
            if c == count:
                return i
    return -1


@njit
def get_nth_index_right(arr: np.ndarray, func, count):
    c = 0
    for i in range(len(arr) - 1, -1, -1):
        if func(arr[i]):
            c += 1
            if c == count:
                return i
    return -1


def _test_get_idx_nb():
    np.random.seed(0)
    arr = np.random.rand(10 ** 7)
    m = 0.999999
    n = 0.9999999
    # # Start of array benchmark
    # % timeit next(iter(np.where(arr > m)[0]), -1)  # 43.5 ms
    # % timeit next((idx for idx, val in enumerate(arr) if val > m), -1)  # 2.5 µs
    # # End of array benchmark
    # % timeit next(iter(np.where(arr > n)[0]), -1)  # 21.4 ms
    # % timeit next((idx for idx, val in enumerate(arr) if val > n), -1)  # 39.2 ms
    idx = get_first_idx_larger_than(arr, n)
    assert idx == -1
    idx = get_first_idx_smaller_than(arr, 1 - n)
    assert idx == 3600965
    idx = get_last_idx_larger_than(arr, n)
    assert idx == -1
    idx = get_last_idx_smaller_than(arr, 1 - n)
    assert idx == 3600965

    idx = get_first_idx_larger_than(arr, m)
    assert idx == 198253
    idx = get_first_idx_smaller_than(arr, 1 - m)
    assert idx == 661553
    idx = get_last_idx_larger_than(arr, m)
    assert idx == 8361873
    idx = get_last_idx_smaller_than(arr, 1 - m)
    assert idx == 6590717

    @njit
    def func(val):
        return val > m

    idx = get_nth_index(arr, func, 2)
    assert idx == 801807
    idx = get_nth_index_right(arr, func, 2)
    assert idx == 8142781


def reduce_list(funx, data_list, initial=None):
    result_list = []

    def reduce_func(x, y):
        # print(x,y)
        result = funx(x, y)
        result_list.append(result)
        return result

    if initial is None:
        reduce(reduce_func, data_list)
    else:
        reduce(reduce_func, data_list, initial)
    return result_list


if __name__ == "__main__":
    pass

    # 测试 chuck 函数
    # a_list = list(range(1, 17))
    # for b_list in split_chunk(a_list, 4):
    #     print(b_list)
    # for b_list in split_chunk(a_list, 5):
    #     print(b_list)
    # for b_list in split_chunk(a_list, 16):
    #     print(b_list)
    # for b_list in split_chunk(a_list, 17):
    #     print(b_list)

    # foo(1, 2, 3, 4, e=5, f=6)
    # _test_get_idx_nb()

