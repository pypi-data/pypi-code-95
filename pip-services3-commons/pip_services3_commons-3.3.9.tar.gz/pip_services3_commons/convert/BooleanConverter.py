# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.BooleanConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Boolean conversion utilities
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional


class BooleanConverter:
    """
    Converts arbitrary values to boolean values using extended conversion __rules:
    - Numbers: <>0 are true, =0 are false
    - Strings: "true", "yes", "T", "Y", "1" are true; "false", "no", "F", "N" are false
    - DateTime: <>0 total milliseconds are true, =0 are false

    Example:
    .. code-block:: python
    
        value1 = BooleanConverter.to_nullable_boolean(true) // true
        value2 = BooleanConverter.to_nullable_boolean("yes") // true
        value3 = BooleanConverter.to_nullable_boolean(123) // true
        value4 = BooleanConverter.to_nullable_boolean({}) // None
    """

    @staticmethod
    def to_nullable_boolean(value: Any) -> Optional[bool]:
        """
        Converts args into boolean or returns None when conversion is not possible.

        :param value: the args to convert.

        :return: boolean args or None when convertion is not supported.
        """
        # Shortcuts
        if value is None:
            return None
        if type(value) is type(True):
            return value

        str_value = str(value).lower()
        # All true values
        if str_value in ['1', 'true', 't', 'yes', 'y']:
            return True
        # All false values
        if str_value in ['0', 'false', 'f', 'no', 'n']:
            return False

        # Everything else:
        return None

    @staticmethod
    def to_boolean(value: Any) -> bool:
        """
        Converts args into boolean or returns false when conversion is not possible.

        :param value: the args to convert.

        :return: boolean args or false when conversion is not supported.
        """
        return BooleanConverter.to_boolean_with_default(value, False)

    @staticmethod
    def to_boolean_with_default(value: Any, default_value: bool) -> bool:
        """
        Converts args into boolean or returns default args when conversion is not possible

        :param value: the args to convert.

        :param default_value: the default args

        :return: boolean args or default when conversion is not supported.
        """
        result = BooleanConverter.to_nullable_boolean(value)
        return result if not (result is None) else default_value
