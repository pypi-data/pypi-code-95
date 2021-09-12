# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.DateTimeConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    DateTime conversion utilities
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from datetime import *
from typing import Any, Optional

import iso8601

from .UTC import UTC


class DateTimeConverter:
    """
    Converts arbitrary values into Date values using extended conversion __rules:
    - Strings: converted using ISO time format
    - Numbers: converted using milliseconds since unix epoch

    Example:
    .. code-block:: python
    
        value1 = DateTimeConverter.to_nullable_datetime("ABC") // Result: None
        value2 = DateTimeConverter.to_nullable_datetime("2018-01-01T11:30:00.0") // Result: Date(2018,0,1,11,30)
        value3 = DateTimeConverter.to_nullable_datetime(123) // Result: Date(123)
    """

    @staticmethod
    def to_nullable_datetime(value: Any) -> Optional[datetime]:
        """
        Converts args into Date or returns null when conversion is not possible.

        :param value: the args to convert.

        :return: Date args or null when conversion is not supported.
        """
        # Shortcuts
        if value is None:
            return None
        if type(value) == datetime:
            return DateTimeConverter.to_utc_datetime(value)

        if type(value) in (int, float, complex):
            value = datetime.fromtimestamp(value)
            return DateTimeConverter.to_utc_datetime(value)
        if type(value) == date:
            value = datetime.combine(value, time(0, 0, 0))
            return DateTimeConverter.to_utc_datetime(value)
        if type(value) == time:
            value = datetime.combine(datetime.utcnow().date, value)
            return DateTimeConverter.to_utc_datetime(value)

        try:
            value = str(value)
            value = iso8601.parse_date(value)
            return DateTimeConverter.to_utc_datetime(value)
        except:
            return None

    @staticmethod
    def to_datetime(value: Any) -> datetime:
        """
        Converts args into Date or returns current date when conversion is not possible.

        :param value: the args to convert.

        :return: Date args or current date when conversion is not supported.
        """
        return DateTimeConverter.to_datetime_with_default(value, None)

    @staticmethod
    def to_datetime_with_default(value: Any, default_value: datetime = None) -> datetime:
        """
        Converts args into Date or returns default when conversion is not possible.

        :param value: the args to convert.

        :param default_value: the default args.

        :return: Date args or default when conversion is not supported.
        """
        result = DateTimeConverter.to_nullable_datetime(value)
        return result if not (result is None) else DateTimeConverter.to_utc_datetime(default_value)

    @staticmethod
    def to_utc_datetime(value: datetime):
        if value is None:
            return value
        elif type(value) == datetime:
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value
        else:
            return DateTimeConverter.to_nullable_datetime(value)
