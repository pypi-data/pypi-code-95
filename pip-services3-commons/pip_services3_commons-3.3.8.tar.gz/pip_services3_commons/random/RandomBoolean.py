# -*- coding: utf-8 -*-
"""
    pip_services3_commons.random.RandomBoolean
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    RandomBoolean implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import random

class RandomBoolean:
    """
    Random generator for boolean values.

    Example:
    
    .. code-block:: python

        value1 = RandomBoolean.next_boolean()   # Possible result: true
        value2 = RandomBoolean.chance(1,3)      # Possible result: false
    """
    @staticmethod
    def chance(chances: float, max_chances: float) -> bool:
        """
        Calculates "chance" out of "max chances".
        Example: 1 chance out of 3 chances (or 33.3%)

        :param chances: a chance proportional to maxChances.

        :param max_chances: a maximum number of chances

        :return: random boolean "chance"
        """
        chances = chances if chances >= 0 else 0
        max_chances = max_chances if max_chances >= 0 else 0
        if chances == 0 and max_chances == 0:
            return False
        
        max_chances = max(max_chances, chances)
        start = (max_chances - chances) / 2
        end = start + chances
        hit = random.random() * max_chances
        return start <= hit <= end

    @staticmethod
    def next_boolean() -> bool:
        """
        Generates a random boolean args.

        :return: a random boolean.
        """
        return random.randint(0, 100) < 50
