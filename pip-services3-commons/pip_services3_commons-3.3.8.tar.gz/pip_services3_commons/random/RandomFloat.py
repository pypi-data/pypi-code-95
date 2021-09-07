# -*- coding: utf-8 -*-
"""
    pip_services3_commons.random.RandomFloat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    RandomFloat implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import random


class RandomFloat:
    """
    Random generator for float values.

    Example:

    .. code-block:: python

        value1 = RandomFloat.next_float(5, 10)     # Possible result: 7.3
        value2 = RandomFloat.next_float(10)        # Possible result: 3.7
        value3 = RandomFloat.update_float(10, 3)   # Possible result: 9.2
    """

    @staticmethod
    def next_float(min: float, max: float = None) -> float:
        if max is None:
            max = min
            min = 0

        if max - min <= 0:
            return min

        return min + random.random() * (max - min)

    @staticmethod
    def update_float(value: float, range: float = None) -> float:
        """
        Updates (drifts) a float args within specified range defined

        :param value: a float args to drift.

        :param range: (optional) a range. Default: 10% of the args

        :return: updated random float args.
        """
        if range is None:
            range = 0.1 * value

        min = value - range
        max = value + range
        return RandomFloat.next_float(min, max)
