from typing import Tuple


def count(arr: list):
    return len(arr) if arr else 0


def average(arr: list):
    return sum(arr) / len(arr) if arr else 0


def bound(arr: list) -> Tuple[int or float, int or float]:
    """
    :return Tuple[max, min]
    """
    if not arr: return None, None
    peak = vale = arr[0]
    for x in arr:
        if x > peak: peak = x
        if x < vale: vale = x
    return peak, vale
