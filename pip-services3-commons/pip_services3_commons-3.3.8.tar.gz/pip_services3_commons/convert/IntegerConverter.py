# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.IntegerConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Integer conversion utilities
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Union, Any, Optional

from pip_services3_commons.convert.LongConverter import LongConverter


class IntegerConverter:
    """
    Converts arbitrary values into integers using extended conversion __rules:
    - Strings are converted to floats, then to integers
    - DateTime: total number of milliseconds since unix epoсh
    - Boolean: 1 for true and 0 for false

    Example:

    .. code-block:: python

        value1 = IntegerConverter.to_nullable_integer("ABC")     # Result: None
        value2 = IntegerConverter.to_nullable_integer("123.456") # Result: 123
        value3 = IntegerConverter.to_nullable_integer(true)      # Result: 1
        value4 = IntegerConverter.to_nullable_integer(datetime.datetime.now()) # Result: current milliseconds
    """

    @staticmethod
    def to_nullable_integer(value: Any) -> Optional[int]:
        """
        Converts args into integer or returns null when conversion is not possible.

        :param value: the args to convert.

        :return: integer args or null when conversion is not supported.
        """
        return LongConverter.to_nullable_long(value)

    @staticmethod
    def to_integer(value: Any) -> int:
        """
        Converts args into integer or returns 0 when conversion is not possible.

        :param value: the args to convert.

        :return: integer args or 0 when conversion is not supported.
        """
        return LongConverter.to_long(value)

    @staticmethod
    def to_integer_with_default(value: Any, default_value: int) -> int:
        """
        Converts args into integer or returns default args when conversion is not possible.

        :param value: the args to convert.

        :param default_value: the default args.

        :return: integer args or default when conversion is not supported.
        """
        return LongConverter.to_long_with_default(value, default_value)
