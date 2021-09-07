# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.RecursiveMapConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Recursive map conversion utilities
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List


class RecursiveMapConverter:
    """
    Converts arbitrary values into map objects using extended conversion __rules.
    This class is similar to :class:`MapConverter <pip_services3_commons.convert.MapConverter.MapConverter>`, but is recursively converts all values stored in objects and arrays.

    Example:

    .. code-block:: python

        value1 = RecursiveMapConverted.to_nullable_map("ABC")        # Result: None
        value2 = RecursiveMapConverted.to_nullable_map({ key: 123 }) # Result: { key: 123 }
        value3 = RecursiveMapConverted.to_nullable_map([1,[2,3])     # Result: { "0": 1, { "0": 2, "1": 3 } }
    """

    @staticmethod
    def __value_to_map(value: Any, classkey=None) -> Any:

        if isinstance(value, dict):
            return RecursiveMapConverter.__map_to_map(value, classkey)

        elif isinstance(value, list):
            return RecursiveMapConverter.__array_to_map(value)

        elif hasattr(value, "_ast"):
            return RecursiveMapConverter.__value_to_map(value._ast())

        elif hasattr(value, "__iter__") and type(value) != str:
            return [RecursiveMapConverter.__value_to_map(v, classkey) for v in value]

        elif hasattr(value, "__dict__"):
            data = {}

            for k in dir(value):
                v = getattr(value, k)
                if not callable(v) and not k.startswith('_'):
                    data[k] = RecursiveMapConverter.__value_to_map(v, classkey)

            if classkey is not None and hasattr(value, "__class__"):
                data[classkey] = value.__class__.__name__
            return data
        else:
            return value

    @staticmethod
    def __array_to_map(value: List[Any]) -> Any:
        result = {}
        try:
            for i in range(len(value)):
                result[i] = RecursiveMapConverter.__value_to_map(value[i])
            return result
        except TypeError:
            return value

    @staticmethod
    def __map_to_map(value: Any, classkey=None) -> Any:
        data = {}
        for (k, v) in value.items():
            data[k] = RecursiveMapConverter.__value_to_map(v, classkey)
        return data

    @staticmethod
    def to_nullable_map(value: Any) -> Any:
        """
        Converts args into map object or returns null when conversion is not possible.

        :param value: the args to convert.

        :return: map object or null when conversion is not supported.
        """
        if value is None:
            return None

        return RecursiveMapConverter.__value_to_map(value)

    @staticmethod
    def to_map(value: Any) -> Any:
        """
        Converts args into map object or returns empty map when conversion is not possible

        :param value: the args to convert.

        :return: map object or empty map when conversion is not supported.
        """
        result = RecursiveMapConverter.to_nullable_map(value)
        return result if result is not None else {}

    @staticmethod
    def to_map_with_default(value: Any, default_value: Any) -> Any:
        """
        Converts args into map object or returns default when conversion is not possible

        :param value: the args to convert.

        :param default_value: the default args.

        :return: map object or emptu map when conversion is not supported.
        """
        result = RecursiveMapConverter.to_nullable_map(value)
        return result if result is not None else default_value
