# -*- coding: utf-8 -*-
"""
    pip_services3_commons.convert.JsonConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Json conversion utilities

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import re
import json
from datetime import datetime
from typing import Any, Optional

from pip_services3_commons.convert.TypeCode import TypeCode
from .MapConverter import MapConverter
from .TypeConverter import TypeConverter


class JsonConverter:
    """
    Converts arbitrary values from and to JSON (JavaScript Object Notation) strings.

    Example:

    .. code-block:: python

        value1 = JsonConverter.from_json("{\"key\":123}") // Result: { key: 123 }
        value2 = JsonConverter.to_map({ key: 123}) // Result: "{\"key\":123}"
    """

    @staticmethod
    def from_json(typ: TypeCode, value: str) -> Any:
        """
        Converts JSON string into a args.

        :param typ: the TypeCode for the data type into which 'args' is to be converted.

        :param value: the JSON string to convert.

        :return: converted object args or null when args is None.
        """
        if value is None:
            return None

        value = json.loads(value, object_hook=JsonConverter.__from_json)
        return TypeConverter.to_type(typ, value)

    @staticmethod
    def to_json(value: Any) -> Optional[str]:
        """
        Converts args into JSON string.

        :param value: the args to convert.

        :return: JSON string or null when args is None.
        """
        if value is None:
            return None

        if isinstance(value, datetime):
            str_time = value.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            return (str_time).split('+')[0] + 'Z'  # Remove microseconds

        return json.dumps(value, default=JsonConverter.__to_json)

    @staticmethod
    def __from_json(obj):
        if not isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(obj[k], list):
                    index = 0
                    for el in obj[k]:
                        obj[k][index] = JsonConverter.__from_json(el)
                        index += 1

                elif isinstance(obj[k], str) and re.match(
                        r"\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z)?", obj[k]):

                    if obj[k][-1].lower() == 'z':
                        obj[k] = obj[k][:-1]
                    obj[k] = datetime.strptime(obj[k], "%Y-%m-%dT%H:%M:%S.%f")

        return obj

    @staticmethod
    def __to_json(obj):
        if obj is None:
            return None

        if isinstance(obj, set):
            obj = list(obj)
        if isinstance(obj, list):
            result = []
            for item in obj:
                item = JsonConverter.__to_json(item)
                result.append(item)
            return result

        if isinstance(obj, dict):
            result = {}
            for (k, v) in obj.items():
                v = JsonConverter.__to_json(v)
                result[k] = v
            return result

        if isinstance(obj, datetime):
            return JsonConverter.to_json(obj)

        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if hasattr(obj, '__dict__'):
            attribs = dict(obj.__dict__)
            dict_obj = {}

            for key in attribs.keys():
                if not (key.endswith('__') and key.startswith('__')):
                    dict_obj[key] = attribs[key]

            return JsonConverter.__to_json(dict_obj)

        return obj

    @staticmethod
    def to_nullable_map(value: str) -> Any:
        """
        Converts JSON string into map object or returns null when conversion is not possible.

        :param value: the JSON string to convert.

        :return: Map object args or null when conversion is not supported.
        """
        if value is None:
            return None

        # Parse JSON
        try:
            value = json.loads(value)
            return MapConverter.to_nullable_map(value)
        except:
            return None

    @staticmethod
    def to_map(value: str) -> Any:
        """
        Converts JSON string into map object or returns empty map when conversion is not possible.

        :param value: the JSON string to convert.

        :return: Map object args or empty object when conversion is not supported.
        """
        result = JsonConverter.to_nullable_map(value)
        return result if not (result is None) else {}

    @staticmethod
    def to_map_with_default(value: str, default_value: Any) -> Any:
        """
        Converts JSON string into map object or returns default args when conversion is not possible.

        :param value: the JSON string to convert.

        :param default_value: the default args.

        :return: Map object args or default when conversion is not supported.
        """
        result = JsonConverter.to_nullable_map(value)
        return result if not (result is None) else default_value
