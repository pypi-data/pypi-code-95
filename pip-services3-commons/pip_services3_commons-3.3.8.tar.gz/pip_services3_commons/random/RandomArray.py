# -*- coding: utf-8 -*-
"""
    pip_services3_commons.random.RandomArray
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    RandomArray implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any

import random




class RandomArray:
    """
    Random generator for array objects.

    Example:
    
    .. code-block:: python

        value1 = RandomArray.pick([1, 2, 3, 4]) # Possible result: 3
    """

    @staticmethod
    def pick(values: List[Any]) -> Any:
        """
        Picks a random element from specified array.

        :param values: an array of any type

        :return: a randomly picked item.
        """
        if values is None or len(values) == 0:
            return None

        return random.choice(values)
