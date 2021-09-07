# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.AnyValueMap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    AnyValueMap implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from datetime import datetime
from typing import Any, List, Optional, Sequence

from pip_services3_commons.convert import DoubleConverter, TypeCode
from pip_services3_commons.data import AnyValue, AnyValueArray
from pip_services3_commons.data.ICloneable import ICloneable
from ..convert.BooleanConverter import BooleanConverter
from ..convert.DateTimeConverter import DateTimeConverter
from ..convert.FloatConverter import FloatConverter
from ..convert.IntegerConverter import IntegerConverter
from ..convert.LongConverter import LongConverter
from ..convert.MapConverter import MapConverter
from ..convert.StringConverter import StringConverter
from ..convert.TypeConverter import TypeConverter




class AnyValueMap(dict, ICloneable):
    """
    Cross-language implementation of dynamic object map (dictionary) what can hold values of any type.
    The stored values can be converted to different types using variety of accessor methods.

    Example:

    .. code-block:: python

        value1 = new AnyValueMap({ key1: 1, key2: "123.456", key3: "2018-01-01" })

        value1.get_as_boolean("key1")   # Result: true
        value1.get_as_integer("key2")   # Result: 123
        value1.get_as_float("key2")     # Result: 123.456
        value1.get_as_datetime("key3")  # Result: new Date(2018,0,1)
    """

    def __init__(self, map: Any = None):
        """
        Creates a new instance of the map and assigns its args.

        :param map: (optional) values to initialize this map.
        """
        super(AnyValueMap, self).__init__()
        self.append(map)

    def get_keys(self) -> List[str]:
        """
        Gets keys of all elements stored in this map.

        :return: a list with all map keys.
        """
        names = []
        for (k, _) in self.items():
            names.append(k)
        return names

    def get(self, key: str) -> Any:
        """
        Gets a map element specified by its key.

        :param key: a key of the element to get.

        :return: the args of the map element.
        """
        return super(AnyValueMap, self).get(key)
        # return self[key] if key in self else None

    def put(self, key: str, value: Any) -> Any:
        """
        Puts a new args into map element specified by its key.

        :param key: a key of the element to put.

        :param value: a new args for map element.
        """
        self[key] = value

    def remove(self, key: str):
        """
        Removes a map element specified by its key

        :param key: a key of the element to remove.
        """
        self.pop(key)

    def append(self, map: Any):
        """
        Appends new elements to this map.

        :param map: a map with elements to be added.
        """
        if isinstance(map, dict):
            for (k, v) in map.items():
                key = StringConverter.to_string(k)
                value = v
                self.put(key, value)

    def clear(self):
        """
        Clears this map by removing all its elements.
        """
        super().clear()

    def length(self) -> int:
        """
        Gets a number of elements stored in this map.

        :return: the number of elements in this map.
        """
        count = 0
        for key in self.keys():
            if key in self.keys() and callable(self[key]):
                count += 1

        return count

    def get_as_object(self, key: str = None) -> Any:
        """
        Gets the args stored in map element without any conversions.
        When element key is not defined it returns the entire map args.

        :param key: (optional) a key of the element to get

        :return: the element args or args of the map when index is not defined.
        """
        if key is None:
            return dict(self)
        else:
            return self.get(key)

    def set_as_object(self, key: Any, value: Any = None):
        """
        Sets a new args to map element specified by its index.
        When the index is not defined, it resets the entire map args.
        This method has double purpose because method overrides are not supported in JavaScript.

        :param key: (optional) a key of the element to set

        :param value: a new element or map args.
        """
        if value is None:
            value = key
            self.clear()
            values = MapConverter.to_map(value)
            self.append(values)
        else:
            self.put(key, value)

    def get_as_map(self, key: str) -> 'AnyValueMap':
        """
        Converts map element into an AnyValueMap or returns empty AnyValueMap if conversion is not possible.

        :param key: a key of element to get.

        :return: AnyValueMap args of the element or empty AnyValueMap if conversion is not supported.
        """
        value = self.get(key)
        return AnyValueMap.from_value(value)

        # if key is None:
        #     map = {}
        #     for (k, v) in self.items():
        #         map[k] = v
        #     return map
        # else:
        #     args = self.get(key)
        #     return MapConverter.to_map(args)

    def set_as_map(self, values):
        """
        Sets values to map

        :param values: values to set
        """
        self.clear()
        for (k, v) in values.items():
            self.put(k, v)

    def get_as_nullable_string(self, key: str) -> str:
        """
        Converts map element into a string or returns None if conversion is not possible.

        :param key: an index of element to get.

        :return: string args of the element or None if conversion is not supported.
        """
        value = self.get(key)
        return StringConverter.to_nullable_string(value)

    def get_as_string(self, key: str) -> str:
        """
        Converts map element into a string or returns "" if conversion is not possible.

        :param key: an index of element to get.

        :return: string args ot the element or "" if conversion is not supported.
        """
        value = self.get(key)
        return StringConverter.to_string(value)

    def get_as_string_with_default(self, key: str, default_value: str) -> str:
        """
        Converts map element into a string or returns default args if conversion is not possible.

        :param key: an index of element to get.

        :param default_value: the default args

        :return: string args ot the element or default args if conversion is not supported.
        """
        value = self.get(key)
        return StringConverter.to_string_with_default(value, default_value)

    def get_as_nullable_boolean(self, key: str) -> Optional[bool]:
        """
        Converts map element into a boolean or returns None if conversion is not possible

        :param key: an index of element to get.

        :return: boolean args of the element or None if conversion is not supported.
        """
        value = self.get(key)
        return BooleanConverter.to_nullable_boolean(value)

    def get_as_boolean(self, key: str) -> bool:
        """
        Converts map element into a boolean or returns false if conversion is not possible.

        :param key: an index of element to get.

        :return: boolean args ot the element or false if conversion is not supported.
        """
        value = self.get(key)
        return BooleanConverter.to_boolean(value)

    def get_as_boolean_with_default(self, key: str, default_value: bool) -> bool:
        """
        Converts map element into a boolean or returns default args if conversion is not possible.

        :param key: an index of element to get.

        :param default_value: the default args

        :return: boolean args ot the element or default args if conversion is not supported.
        """
        value = self.get(key)
        return BooleanConverter.to_boolean_with_default(value, default_value)

    def get_as_nullable_integer(self, key: str) -> Optional[int]:
        """
        Converts map element into an integer or returns None if conversion is not possible.

        :param key: an index of element to get.

        :return: integer args of the element or None if conversion is not supported.
        """
        value = self.get(key)
        return IntegerConverter.to_nullable_integer(value)

    def get_as_integer(self, key: str) -> int:
        """
        Converts map element into an integer or returns 0 if conversion is not possible.

        :param key: an index of element to get.

        :return: integer args ot the element or 0 if conversion is not supported.
        """
        value = self.get(key)
        return IntegerConverter.to_integer(value)

    def get_as_integer_with_default(self, key: str, default_value: int) -> int:
        """
        Converts map element into an integer or returns default args if conversion is not possible.

        :param key: an index of element to get.

        :param default_value: the default args

        :return: integer args ot the element or default args if conversion is not supported.
        """
        value = self.get(key)
        return IntegerConverter.to_integer_with_default(value, default_value)

    def get_as_nullable_long(self, key: str) -> Optional[float]:
        value = self.get(key)
        return LongConverter.to_nullable_long(value)

    def get_as_long(self, key: str) -> float:
        value = self.get(key)
        return LongConverter.to_long(value)

    def get_as_long_with_default(self, key: str, default_value: float) -> float:
        value = self.get(key)
        return LongConverter.to_long_with_default(value, default_value)

    def get_as_nullable_float(self, key: str) -> Optional[float]:
        """
        Converts map element into a float or returns None if conversion is not possible.

        :param key: an index of element to get.

        :return: float args of the element or None if conversion is not supported.
        """
        value = self.get(key)
        return FloatConverter.to_nullable_float(value)

    def get_as_float(self, key: str) -> float:
        """
        Converts map element into a float or returns 0 if conversion is not possible.

        :param key: an index of element to get.

        :return: float args ot the element or 0 if conversion is not supported.
        """
        value = self.get(key)
        return FloatConverter.to_float(value)

    def get_as_float_with_default(self, key: str, default_value: float) -> float:
        """
        Converts map element into a float or returns default args if conversion is not possible.

        :param key: an index of element to get.

        :param default_value: the default args

        :return: float args ot the element or default args if conversion is not supported.
        """
        value = self.get(key)
        return FloatConverter.to_float_with_default(value, default_value)

    def get_as_nullable_double(self, key: str) -> Optional[float]:
        """
        Converts map element into a float or returns None if conversion is not possible.

        :param key: an index of element to get.

        :return: float args of the element or None if conversion is not supported.
        """
        value = self.get(key)
        return DoubleConverter.to_nullable_double(value)

    def get_as_double(self, key: str) -> float:
        """
        Converts map element into a float or returns 0 if conversion is not possible.

        :param key: an index of element to get.

        :return: float args ot the element or 0 if conversion is not supported.
        """
        return self.get_as_double_with_default(key, 0)

    def get_as_double_with_default(self, key: str, default_value: float) -> float:
        """
        Converts map element into a float or returns default args if conversion is not possible.

        :param key: an index of element to get.

        :param default_value: the default args

        :return: float args ot the element or default args if conversion is not supported.
        """
        value = self.get(key)
        return DoubleConverter.to_double_with_default(value, default_value)

    def get_as_nullable_datetime(self, key: str) -> Optional[datetime]:
        """
        Converts map element into a Date or returns None if conversion is not possible.

        :param key: an index of element to get.

        :return: Date args of the element or None if conversion is not supported.
        """
        value = self.get(key)
        return DateTimeConverter.to_nullable_datetime(value)

    def get_as_datetime(self, key: str) -> datetime:
        """
        Converts map element into a Date or returns the current date if conversion is not possible.

        :param key: an index of element to get.

        :return: Date args ot the element or the current date if conversion is not supported.
        """
        value = self.get(key)
        return DateTimeConverter.to_datetime(value)

    def get_as_datetime_with_default(self, key: str, default_value: datetime) -> datetime:
        """
        Converts map element into a Date or returns default args if conversion is not possible.

        :param key: an index of element to get.

        :param default_value: the default args

        :return: Date args ot the element or default args if conversion is not supported.
        """
        value = self.get(key)
        return DateTimeConverter.to_datetime_with_default(value, default_value)

    def get_as_nullable_type(self, value_type: TypeCode, key: str) -> Any:
        """
        Converts map element into a args defined by specied typecode.
        If conversion is not possible it returns None.

        :param value_type: the TypeCode that defined the type of the result
        :param key: an index of element to get.

        :return: element args defined by the typecode or None if conversion is not supported.
        """
        value = self.get(key)
        return TypeConverter.to_nullable_type(value_type, value)

    def get_as_type(self, value_type: TypeCode, key: str) -> Any:
        """
        Converts map element into a args defined by specied typecode.
        If conversion is not possible it returns default args for the specified type.

        :param value_type: the TypeCode that defined the type of the result
        :param key: an index of element to get.

        :return: element args defined by the typecode or default if conversion is not supported.
        """
        value = self.get(key)
        return TypeConverter.to_type(value_type, value)

    def get_as_type_with_default(self, value_type: TypeCode, key: str, default_value: Any) -> Any:
        """
        Converts map element into a args defined by specied typecode.
        If conversion is not possible it returns default args.

        :param value_type: the TypeCode that defined the type of the result
        :param key: an index of element to get.
        :param default_value: the default args

        :return: element args defined by the typecode or default args if conversion is not supported.
        """
        value = self.get(key)
        return TypeConverter.to_type_with_default(value_type, value, default_value)

    def get_as_value(self, key: str) -> AnyValue:
        """
        Converts map element into an AnyValue or returns an empty AnyValue if conversion is not possible.

        :param key: a key of element to get.
        :return: AnyValue value of the element or empty AnyValue if conversion is not supported.
        """
        value = self.get(key)
        return AnyValue(value)

    def get_as_array(self, key: str) -> AnyValueArray:
        """
        Converts map element into an :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` or returns empty :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` if conversion is not possible.

        :param key: an index of element to get.

        :return: :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` args of the element or empty :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` if conversion is not supported.
        """
        value = self.get(key)
        return AnyValueArray.from_value(value)

    def get_as_nullable_map(self, key: str) -> Optional['AnyValueMap']:
        """
        Converts map element into an :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` or returns None if conversion is not possible.

        :param key: a key of element to get.

        :return: :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` args of the element or None if conversion is not supported.
        """
        value = self.get_as_object(key)
        return AnyValueMap.from_value(value)

    # def get_as_map(self, key):
    #     args = self.get(key)
    #     return self.from_value(args)

    def get_as_map_with_default(self, key: str, default_value: 'AnyValueMap') -> 'AnyValueMap':
        """
        Converts map element into an AnyValueMap or returns default args if conversion is not possible.

        :param key: a key of element to get.

        :param default_value: the default args

        :return: :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` args of the element or default args if conversion is not supported.
        """
        value = self.get_as_nullable_map(key)
        return MapConverter.to_map_with_default(value, default_value)

    def contains_key(self, key):
        return key in self

    def clone(self) -> Any:
        """
        Creates a binary clone of this object.

        :return: a clone of this object.
        """
        map = AnyValueMap()
        map.set_as_map(self)
        return map

    def to_string(self) -> str:
        """
        Gets a string representation of the object.
        The result is a semicolon-separated list of key-args pairs as
        **"key1=value1;key2=value2;key=value3"**

        :return: a string representation of the object.
        """
        result = ''

        for (key, value) in self.items():
            if len(result) > 0:
                result += ';'

            if not (value is None):
                result += key + '=' + StringConverter.to_string_with_default(value, '')
            else:
                result += key

        return result

    def __str__(self):
        """
        Gets a string representation of the object.
        The result is a semicolon-separated list of key-args pairs as
        **"key1=value1;key2=value2;key=value3"**

        :return: a string representation of the object.
        """
        result = ''

        for (key, value) in self.items():
            if len(result) > 0:
                result += ';'

            if not (value is None):
                result += key + '=' + StringConverter.to_string_with_default(value, '')
            else:
                result += key

        return result

    @staticmethod
    def from_value(value: Any) -> 'AnyValueMap':
        """
        Converts specified args into AnyValueMap.

        :param value: args to be converted

        :return: a newly created AnyValueMap.
        """
        map = AnyValueMap()
        map.set_as_object(value)
        return map

    @staticmethod
    def from_tuples(*tuples: Any) -> 'AnyValueMap':
        """
        Creates a new AnyValueMap from a list of key-args pairs called tuples.

        :param tuples: a list of values where odd elements are keys and the following even elements are values

        :return: a newly created :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>`.
        """
        return AnyValueMap.from_tuples_array(tuples)

    @staticmethod
    def from_tuples_array(tuples: Sequence[Any]) -> 'AnyValueMap':
        """
        Creates a new AnyValueMap from a list of key-args pairs called tuples.
        The method is similar to :func:`from_tuples` but tuples are passed as array instead of parameters.

        :param tuples: a list of values where odd elements are keys and the following even elements are values

        :return: a newly created :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>`.
        """
        result = AnyValueMap()

        if tuples is None or len(tuples) == 0:
            return result

        index = 0
        while index < len(tuples):
            if index + 1 >= len(tuples):
                break

            key = StringConverter.to_string(tuples[index])
            value = tuples[index + 1]
            index += 2

            result.put(key, value)

        return result

    @staticmethod
    def from_maps(*maps: dict) -> 'AnyValueMap':
        """
        Creates a new AnyValueMap by merging two or more maps.
        Maps defined later in the list override values from previously defined maps.

        :param maps: an array of maps to be merged

        :return: a newly created :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>`.
        """
        result = AnyValueMap()

        if maps is None or len(maps) == 0:
            return result

        for map in maps:
            for (key, value) in map.items():
                key = StringConverter.to_string(key)
                result.put(key, value)

        return result
