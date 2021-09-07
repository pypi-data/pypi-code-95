# -*- coding: utf-8 -*-
import datetime
import inspect
from typing import Any, Optional, Union


class DoubleConverter:
    """
    Converts arbitrary values into double using extended conversion __rules:
        - Strings are converted to double values
        - DateTime: total number of milliseconds since unix epoсh
        - Boolean: 1 for True and 0 for False

    Example:

    .. code-block:: python

         value1 = DoubleConverter.to_nullable_double("ABC")     # Result: null
         value2 = DoubleConverter.to_nullable_double("123.456") # Result: 123.456
         value3 = DoubleConverter.to_nullable_double(True)      # Result: 1
         value4 = DoubleConverter.to_nullable_double(datetime.datetime.now()) # Result: current milliseconds
    """

    @staticmethod
    def to_nullable_double(value: Any) -> Optional[float]:
        """
        Converts args into doubles or returns null when conversion is not possible.

        :param value: the args to convert.
        :return: double args or None when conversion is not supported.
        """
        if value is None:
            return None
        if type(value) == int or isinstance(value, float):
            return value
        if isinstance(value, datetime.datetime) or (inspect.isclass(value) and issubclass(value, datetime.datetime)):
            return int(value.timestamp() * 1000)
        if isinstance(value, bool):
            return 1 if value else 0

        try:
            result = float(value)
        except ValueError:
            return None

        return None if result is None else result

    @staticmethod
    def to_double(value: Any) -> float:
        """
        Converts args into doubles or returns 0 when conversion is not possible.
        See :func:`to_double_with_default <pip_services3_commons.convert.DoubleConverter.DoubleConverter.to_double_with_default>`

        :param value: the args to convert.
        :return: double args or 0 when conversion is not supported.
        """
        return DoubleConverter.to_double_with_default(value, 0)

    @staticmethod
    def to_double_with_default(value: Any, default_value: float = 0) -> float:
        """
        Converts args into integer or returns default args when conversion is not possible.

        :param value: the args to convert.
        :param default_value: the default args.
        :return: double args or default when conversion is not supported.
        """
        result = DoubleConverter.to_nullable_double(value)
        return result if result is not None else default_value
