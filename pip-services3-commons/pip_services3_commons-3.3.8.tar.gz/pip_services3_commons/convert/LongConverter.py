# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.LongConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Long conversion utilities
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import inspect
from datetime import datetime
from typing import Any, Optional


class LongConverter:
    """
    Converts arbitrary values into longs using extended conversion __rules:
        - Strings are converted to floats, then to longs
        - DateTime: total number of milliseconds since unix epoсh
        - Boolean: 1 for true and 0 for false
    """

    @staticmethod
    def to_nullable_long(value: Any) -> Optional[float]:
        """
        Converts value into long or returns null when conversion is not possible.

        :param value: the value to convert.
        :return: long value or null when conversion is not supported.
        """
        if value is None:
            return None
        if type(value) == int or isinstance(value, float):
            return int(value)
        if isinstance(value, datetime) or inspect.isclass(value) and issubclass(value, datetime):
            return int(value.timestamp() * 1000)
        if isinstance(value, bool):
            return 1 if value else 0

        try:
            result = float(value)
        except ValueError:
            return None

        return None if result is None else int(result)

    @staticmethod
    def to_long(value: Any) -> float:
        """
        Converts value into long or returns 0 when conversion is not possible.

        :param value: the value to convert.
        :return: long value or 0 when conversion is not supported.
        """
        return LongConverter.to_long_with_default(value, 0)

    @staticmethod
    def to_long_with_default(value: Any, default_value: float) -> float:
        """
        Converts value into integer or returns default when conversion is not possible.

        :param value: the value to convert.
        :param default_value: the default value.
        :return: long value or default when conversion is not supported
        """
        result = LongConverter.to_nullable_long(value)
        return result if not (result is None) else default_value
