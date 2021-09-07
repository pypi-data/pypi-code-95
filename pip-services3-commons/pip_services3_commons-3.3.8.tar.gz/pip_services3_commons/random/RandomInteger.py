# -*- coding: utf-8 -*-
"""
    pip_services3_commons.random.RandomInteger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Random integer implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Union, List

import random


class RandomInteger:
    """
    Random generator for integer values.

    Example:
    
    .. code-block:: python

        value1 = RandomInteger.next_integer(5, 10)     # Possible result: 7
        value2 = RandomInteger.next_integer(10)        # Possible result: 3
        value3 = RandomInteger.update_integer(10, 3)   # Possible result: 9
    """

    @staticmethod
    def next_integer(min: int, max: int = None) -> int:
        """
        Generates a integer in the range ['min', 'max']. If 'max' is omitted, then the range will be set to [0, 'min'].

        :param min: minimum args of the integer that will be generated.
                   If 'max' is omitted, then 'max' is set to 'min' and 'min' is set to 0.

        :param max: (optional) maximum args of the float that will be generated. Defaults to 'min' if omitted.

        :return: generated random integer args.
        """
        if max is None:
            max = min
            min = 0

        if max - min <= 0:
            return min

        return random.randint(min, max - 1)

    @staticmethod
    def update_integer(value: int, range: int = None) -> int:
        """
        Updates (drifts) a integer args within specified range defined

        :param value: a integer args to drift.

        :param range: (optional) a range. Default: 10% of the args

        :return: updated integer args.
        """
        if range is None:
            range = int(0.1 * value)

        min = value - range
        max = value + range
        return RandomInteger.next_integer(min, max)

    @staticmethod
    def sequence(min: int, max: int = None) -> List[int]:
        """
        Generates a random sequence of integers starting from 0 like: [0,1,2,3...??]

        :param min: minimum args of the integer that will be generated.
                   If 'max' is omitted, then 'max' is set to 'min' and 'min' is set to 0.

        :param max: (optional) maximum args of the float that will be generated. Defaults to 'min' if omitted.

        :return: generated array of integers.
        """
        max = max if max is not None else min
        count = RandomInteger.next_integer(min, max)
        return list(range(count))
