# -*- coding: utf-8 -*-
from typing import Union

from random import random


class RandomDouble:
    """
    Random generator for double values.

    Example:

    .. code-block:: python

        value1 = RandomDouble.next_double(5, 10)     # Possible result: 7.3
        value2 = RandomDouble.next_double(10)        # Possible result: 3.7
        value3 = RandomDouble.next_double(10, 3)     # Possible result: 9.2
    """

    @staticmethod
    def next_double(mmin: float, mmax: float = None) -> float:
        """
        Generates a random double args in the range ['minYear', 'maxYear'].

        :param mmin: (optional) minimum range args
        :param mmax: max range args
        :return: a random double args.
        """
        if mmax is None:
            mmax = mmin
            mmin = 0

        if mmax - mmin < 0:
            return mmin

        return mmin + random() * (mmax - mmin)

    @staticmethod
    def update_double(value: float, rrange: float = None) -> float:
        """
        Updates (drifts) a double args within specified range defined

        :param rrange:
        :param value: a double args to drift.
        :param range: (optional) a range. Default: 10% of the args
        """
        if rrange is None:
            rrange = 0

        rrange = 0.1 * value if rrange == 0 else rrange
        min_val = value - rrange
        max_val = value + rrange
        return RandomDouble.next_double(min_val, max_val)
