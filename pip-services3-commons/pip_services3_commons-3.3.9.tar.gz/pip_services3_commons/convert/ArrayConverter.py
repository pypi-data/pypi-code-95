# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.ArrayConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Array conversion utilities

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional


class ArrayConverter:
    """
    Converts arbitrary values into array objects.
    Example:

    .. code-block:: python

        value1 = ArrayConverter.to_array([1, 2])       # Result: [1, 2]
        value2 = ArrayConverter.to_array(1)            # Result: [1]
        value2 = ArrayConverter.list_to_array("1,2,3") # Result: ["1", "2", "3"]

    """

    @staticmethod
    def to_nullable_array(value: Any) -> Optional[List[Any]]:
        """
        Converts args into array object.
        Single values are converted into arrays with a single element.

        :param value: the args to convert.

        :return: array object or None when args is None.
        """
        # Shortcuts
        if value is None:
            return None
        if type(value) == list:
            return value

        if type(value) in [tuple, set]:
            return list(value)

        if isinstance(value, dict):
            array = []
            for prop in value.keys():
                array.append(value[prop])
            return array

        if hasattr(value, '__dict__'):
            array = []
            for prop in value.__dict__.keys():
                array.append(value[prop])
            return array

        # Convert single values
        return [value]

    @staticmethod
    def to_array(value: Any) -> Any:
        """
        Converts args into array object with empty array as default.
        Single values are converted into arrays with single element.

        :param value: the args to convert.

        :return: array object or empty array when args is None.
        """
        return ArrayConverter.to_array_with_default(value, [])

    @staticmethod
    def to_array_with_default(value: Any, default_value: List[Any]) -> List[Any]:
        """
        Converts args into array object with specified default.
        Single values are converted into arrays with single element.

        :param value: the args to convert.

        :param default_value: default array object.

        :return: array object or default array when args is None.
        """
        result = ArrayConverter.to_nullable_array(value)
        return result if not (result is None) else default_value

    @staticmethod
    def list_to_array(value: Any) -> List[Any]:
        """
        Converts args into array object with empty array as default.
        Strings with comma-delimited values are split into array of strings.

        :param value: the list to convert.

        :return: array object or empty array when args is None
        """
        if value is None:
            return []
        elif type(value) in [list, tuple, set]:
            return list(value)
        elif type(value) in [str]:
            return value.split(',')
        else:
            return ArrayConverter.to_array(value)
