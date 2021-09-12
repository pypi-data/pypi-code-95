# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.MapConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Map conversion utilities
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any


class MapConverter:
    """
    Converts arbitrary values into map objects using extended conversion __rules:
    - Objects: property names as keys, property values as values
    - Arrays: element indexes as keys, elements as values

    Example:

    .. code-block:: python
    
        value1 = MapConverter.to_nullable_map("ABC") // Result: None
        value2 = MapConverter.to_nullable_map({ key: 123 }) // Result: { key: 123 }
        value3 = MapConverter.to_nullable_map([1,2,3]) // Result: { "0": 1, "1": 2, "2": 3 }
    """
    @staticmethod
    def to_nullable_map(value: Any) -> Any:
        """
        Converts args into map object or returns null when conversion is not possible.

        :param value: the args to convert.

        :return: map object or null when conversion is not supported.
        """
        if isinstance(value, dict):
            return value
        elif hasattr(value, "_ast"):
            return value._ast()
        elif hasattr(value, "__iter__") and not isinstance(value, str):
            data = {}
            index = 0
            for v in value:
                data[str(index)] = v
                index += 1
            return data
        elif hasattr(value, "__dict__"):
            data = {} 
            for k in dir(value):
                v = getattr(value, k) 
                if not callable(v) and not k.startswith('_'):
                    data[k] = v
            return data
        else:
            return None

        #return MapConverter.to_map(args)

    @staticmethod
    def to_map(value: Any) -> Any:
        """
        Converts args into map object or returns empty map when conversion is not possible

        :param value: the args to convert.

        :return: map object or empty map when conversion is not supported.
        """
        result = MapConverter.to_nullable_map(value)
        return result if not (result is None) else {}

    @staticmethod
    def to_map_with_default(value: Any, default_value: Any) -> Any:
        """
        Converts args into map object or returns default when conversion is not possible

        :param value: the args to convert.

        :param default_value: the default args.

        :return: map object or emptu map when conversion is not supported.
        """
        result = MapConverter.to_nullable_map(value)
        return result if not (result is None) else default_value
