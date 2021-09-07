# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.AnyValueArray
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    AnyValueArray implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from datetime import datetime
from typing import List, Any, Optional, Sequence

from pip_services3_commons.convert import DoubleConverter, TypeCode
from pip_services3_commons.data import AnyValue, AnyValueMap
from pip_services3_commons.data.ICloneable import ICloneable
from ..convert.ArrayConverter import ArrayConverter
from ..convert.BooleanConverter import BooleanConverter
from ..convert.DateTimeConverter import DateTimeConverter
from ..convert.FloatConverter import FloatConverter
from ..convert.IntegerConverter import IntegerConverter
from ..convert.LongConverter import LongConverter
from ..convert.StringConverter import StringConverter
from ..convert.TypeConverter import TypeConverter




class AnyValueArray(list, ICloneable):
    """
    Cross-language implementation of dynamic object array what can hold values of any type.
    The stored values can be converted to different types using variety of accessor methods.

    Example:

    .. code-block:: python

        value1 = AnyValueArray([1, "123.456", "2018-01-01"])
        value1.get_as_boolean(0)   # Result: true
        value1.get_as_integer(1)   # Result: 123
        value1.get_as_float(1)     # Result: 123.456
        value1.get_as_datetime(2)  # Result: datetime.datetime(2018,0,1)
    """

    def __init__(self, values: Sequence[Any] = None):
        """
        Creates a new instance of the array and assigns its args.

        :param values: (optional) values to initialize this array.
        """
        super(AnyValueArray, self).__init__()
        if values is not None and len(values) > 0:
            for value in values:
                self.append(value)

    def get(self, index: int) -> Any:
        """
        Gets an array element specified by its index.

        :param index: an index of the element to get.
        :return: the value of the array element.
        """
        return self[index]

    def put(self, index: int, value: Any):
        """
        Puts a new value into array element specified by its index.

        :param index: a new value for array element.
        :param value: an index of the element to put.
        :return: the value of the array element.
        """
        self[index] = value

    def remove(self, index: int):
        """
        Removes an array element specified by its index

        :param index: an index of the element to remove.
        """
        del self[index]

    def appends(self, elements: List[Any]):
        """
        Appends new elements to this array.

        :param elements: a list of elements to be added.
        """
        if elements is not None:
            for element in elements:
                self.append(element)

    def clear(self):
        """
        Clears this array by removing all its elements.
        """
        del self[:]

    def get_as_object(self, index: int = None) -> Any:
        """
        Gets the args stored in array element without any conversions.
        When element index is not defined it returns the entire array args.

        :param index: (optional) an index of the element to get

        :return: the element args or args of the array when index is not defined.
        """
        if index is None:
            return self.get_as_array(index)
        else:
            return self[index]

    def set_as_object(self, index: int = None, value: Any = None):
        """
        Sets a new args to array element specified by its index.
        When the index is not defined, it resets the entire array args.
        This method has double purpose because method overrides are not supported in JavaScript.

        :param index: (optional) an index of the element to set

        :param value: a new element or array args.
        """
        if index is None and not (value is None):
            self.set_as_array(value)
        else:
            self[index] = value

    def get_as_array(self, index: int) -> 'AnyValueArray':
        """
        Converts array element into an :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>` or returns empty :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>` if conversion is not possible.

        :param index: an index of element to get.

        :return: :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>` args of the element or empty :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>` if conversion is not supported.
        """
        if index is None:
            array = []
            for value in self:
                array.append(value)
            return array
        else:
            value = self[index]
            return AnyValueArray.from_value(value)

    def get_as_nullable_array(self, index: int) -> Optional['AnyValueArray']:
        """
        Converts array element into an AnyValueArray or returns null if conversion is not possible.

        :param index: an index of element to get.
        :return: AnyValueArray value of the element or null if conversion is not supported.
        """
        value = self[index]
        return AnyValueArray.from_value(value) if value is not None else None

    def get_as_array_with_default(self, index: int, default_value: 'AnyValueArray') -> 'AnyValueArray':
        """
        Converts array element into an AnyValueArray or returns default value if conversion is not possible.

        :param index: an index of element to get.
        :param default_value: the default value
        :return: AnyValueArray value of the element or default value if conversion is not supported.
        """

        result = self.get_as_nullable_array(index)
        return result if result is not None else default_value

    def set_as_array(self, values: List[Any]):
        """
        Sets a new values to array element

        :param values: values to set
        """
        del self[:]
        for value in values:
            self.append(value)

    def get_as_nullable_string(self, index: int) -> Optional[str]:
        """
        Converts array element into a string or returns None if conversion is not possible.

        :param index: an index of element to get.

        :return: string args of the element or None if conversion is not supported.
        """
        value = self[index]
        return StringConverter.to_nullable_string(value)

    def get_as_string(self, index: int) -> str:
        """
        Converts array element into a string or returns "" if conversion is not possible.

        :param index: an index of element to get.

        :return: string args ot the element or "" if conversion is not supported.
        """
        value = self[index]
        return StringConverter.to_string(value)

    def get_as_string_with_default(self, index: int, default_value: str) -> str:
        """
        Converts array element into a string or returns default args if conversion is not possible.

        :param index: an index of element to get.

        :param default_value: the default args

        :return: string args ot the element or default args if conversion is not supported.
        """
        value = self[index]
        return StringConverter.to_string_with_default(value, default_value)

    def get_as_nullable_boolean(self, index: int) -> Optional[bool]:
        """
        Converts array element into a boolean or returns None if conversion is not possible

        :param index: an index of element to get.

        :return: boolean args of the element or None if conversion is not supported.
        """
        value = self[index]
        return BooleanConverter.to_nullable_boolean(value)

    def get_as_boolean(self, index: int) -> bool:
        """
        Converts array element into a boolean or returns false if conversion is not possible.

        :param index: an index of element to get.

        :return: boolean args ot the element or false if conversion is not supported.
        """
        value = self[index]
        return BooleanConverter.to_boolean(value)

    def get_as_boolean_with_default(self, index: int, default_value: bool) -> bool:
        """
        Converts array element into a boolean or returns default args if conversion is not possible.

        :param index: an index of element to get.

        :param default_value: the default args

        :return: boolean args ot the element or default args if conversion is not supported.
        """
        value = self[index]
        return BooleanConverter.to_boolean_with_default(value, default_value)

    def get_as_nullable_integer(self, index: int) -> Optional[int]:
        """
        Converts array element into an integer or returns None if conversion is not possible.

        :param index: an index of element to get.

        :return: integer args of the element or None if conversion is not supported.
        """
        value = self[index]
        return IntegerConverter.to_nullable_integer(value)

    def get_as_integer(self, index) -> int:
        """
        Converts array element into an integer or returns 0 if conversion is not possible.

        :param index: an index of element to get.

        :return: integer args ot the element or 0 if conversion is not supported.
        """
        value = self[index]
        return IntegerConverter.to_integer(value)

    def get_as_integer_with_default(self, index: int, default_value: int) -> int:
        """
        Converts array element into an integer or returns default args if conversion is not possible.

        :param index: an index of element to get.

        :param default_value: the default args

        :return: integer args ot the element or default args if conversion is not supported.
        """
        value = self[index]
        return IntegerConverter.to_integer_with_default(value, default_value)

    def get_as_nullable_long(self, index: int) -> float:
        value = self[index]
        return LongConverter.to_nullable_long(value)

    def get_as_long(self, index: int) -> float:
        value = self[index]
        return LongConverter.to_long(value)

    def get_as_long_with_default(self, index: int, default_value: float) -> float:
        value = self[index]
        return LongConverter.to_long_with_default(value, default_value)

    def get_as_nullable_float(self, index: int) -> Optional[float]:
        """
        Converts array element into a float or returns None if conversion is not possible.

        :param index: an index of element to get.

        :return: float args of the element or None if conversion is not supported.
        """
        value = self[index]
        return FloatConverter.to_nullable_float(value)

    def get_as_float(self, index: int) -> float:
        """
        Converts array element into a float or returns 0 if conversion is not possible.

        :param index: an index of element to get.

        :return: float args ot the element or 0 if conversion is not supported.
        """
        value = self[index]
        return FloatConverter.to_float(value)

    def get_as_float_with_default(self, index: int, default_value: float) -> float:
        """
        Converts array element into a float or returns default args if conversion is not possible.

        :param index: an index of element to get.

        :param default_value: the default args

        :return: float args ot the element or default args if conversion is not supported.
        """
        value = self[index]
        return FloatConverter.to_float_with_default(value, default_value)

    def get_as_nullable_double(self, index: int) -> float:
        """
        Converts array element into a double or returns null if conversion is not possible.

        :param index: an index of element to get.
        :return: double value of the element or null if conversion is not supported.
        """
        value = self[index]
        return DoubleConverter.to_nullable_double(value)

    def get_as_double(self, index: int) -> float:
        """
        Converts array element into a double or returns 0 if conversion is not possible.

        :param index: an index of element to get.
        :return: double value ot the element or 0 if conversion is not supported.
        """
        return self.get_as_double_with_default(index, 0)

    def get_as_double_with_default(self, index: int, default_value: float) -> float:
        """
        Converts array element into a double or returns default value if conversion is not possible.

        :param index: an index of element to get.
        :param default_value: the default value
        :return: double value ot the element or default value if conversion is not supported.
        """

    def get_as_nullable_datetime(self, index: int) -> Optional[datetime]:
        """
        Converts array element into a Date or returns None if conversion is not possible.

        :param index: an index of element to get.

        :return: Date args of the element or None if conversion is not supported.
        """
        value = self[index]
        return DateTimeConverter.to_nullable_datetime(value)

    def get_as_datetime(self, index: int) -> datetime:
        """
        Converts array element into a Date or returns the current date if conversion is not possible.

        :param index: an index of element to get.

        :return: Date args ot the element or the current date if conversion is not supported.
        """
        value = self[index]
        return DateTimeConverter.to_datetime(value)

    def get_as_datetime_with_default(self, index: int, default_value: datetime) -> datetime:
        """
        Converts array element into a Date or returns default args if conversion is not possible.

        :param index: an index of element to get.

        :param default_value: the default args

        :return: Date args ot the element or default args if conversion is not supported.
        """
        value = self[index]
        return DateTimeConverter.to_datetime_with_default(value, default_value)

    def get_as_nullable_type(self, value_type: TypeCode, index: int) -> Any:
        """
        Converts array element into a args defined by specied typecode.
        If conversion is not possible it returns None.

        :param value_type: the TypeCode that defined the type of the result

        :param index: an index of element to get.

        :return: element args defined by the typecode or None if conversion is not supported.
        """
        value = self[index]
        return TypeConverter.to_nullable_type(value_type, value)

    def get_as_type(self, value_type: TypeCode, index: int) -> Any:
        """
        Converts array element into a args defined by specied typecode.
        If conversion is not possible it returns default args for the specified type.

        :param value_type: the TypeCode that defined the type of the result
        :param index: an index of element to get.

        :return: element args defined by the typecode or default if conversion is not supported.
        """
        value = self[index]
        return TypeConverter.to_type(value_type, value)

    def get_as_type_with_default(self, value_type: TypeCode, index: int, default_value: Any) -> Any:
        """
        Converts array element into a args defined by specied typecode.
        If conversion is not possible it returns default args.

        :param value_type: the TypeCode that defined the type of the result
        :param index: an index of element to get.
        :param default_value: the default args

        :return: element args defined by the typecode or default args if conversion is not supported.
        """
        value = self[index]
        return TypeConverter.to_type_with_default(value_type, value, default_value)

    # def get_as_array(self, index):
    #     args = self[index]
    #     return AnyValueArray.from_value(args)

    def get_as_value(self, index: int) -> 'AnyValue':
        """
        Converts array element into an AnyValue or returns an empty AnyValue if conversion is not possible.

        :param index: an index of element to get.

        :return: AnyValue args of the element or empty AnyValue if conversion is not supported.
        """
        value = self[index]
        return AnyValue(value)

    def get_as_map(self, index: int) -> AnyValueMap:
        """
        Converts array element into an :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` or returns empty :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` if conversion is not possible.

        :param index: an index of element to get.

        :return: :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` args of the element or empty :class:`AnyValueMap <pip_services3_commons.data.AnyValueMap.AnyValueMap>` if conversion is not supported.
        """
        value = self[index]
        return AnyValueMap.from_value(value)

    def get_as_nullable_map(self, index: int) -> Optional['AnyValueMap']:
        """
        Converts array element into an AnyValueMap or returns null if conversion is not possible.

        :param index: an index of element to get.
        :return: AnyValueMap value of the element or null if conversion is not supported.
        """
        value = self[index]
        return AnyValueMap.from_value(value) if value is not None else None

    def get_as_map_with_default(self, index: int, default_value: AnyValueMap) -> AnyValueMap:
        """
        Converts array element into an AnyValueMap or returns default value if conversion is not possible.

        :param index: an index of element to get.
        :param default_value: the default value
        :return: AnyValueMap value of the element or default value if conversion is not supported.
        """
        result = self.get_as_nullable_map(index)
        return AnyValueMap.from_value(result) if result is not None else default_value

    def contains(self, value: Any) -> bool:
        """
        Checks if this array contains a args.
        The check uses direct comparison between elements and the specified args.

        :param value: a args to be checked

        :return: true if this array contains the args or false otherwise.
        """
        str_value = StringConverter.to_nullable_string(value)

        for element in self:
            str_element = StringConverter.to_string(element)

            if str_value is None and str_element is None:
                return True
            if str_value is None or str_element is None:
                continue

            if str_value == str_element:
                return True

        return False

    def contains_as_type(self, value_type: TypeCode, value: Any) -> bool:
        """
        Checks if this array contains a args.
        The check before comparison converts elements and the args to type specified by type code.

        :param value_type: a type code that defines a type to convert values before comparison

        :param value: a args to be checked

        :return: true if this array contains the args or false otherwise.
        """
        typed_value = TypeConverter.to_nullable_type(value_type, value)

        for element in self:
            typed_element = TypeConverter.to_type(value_type, element)

            if typed_value is None and typed_element is None:
                return True
            if typed_value is None or typed_element is None:
                continue

            if typed_value == typed_element:
                return True

        return False

    def clone(self) -> Any:
        """
        Creates a binary clone of this object.

        :return: a clone of this object.
        """
        array = AnyValueArray()
        array.set_as_array(self)
        return array

    def to_string(self) -> str:
        """
        Gets a string representation of the object.
        The result is a comma-separated list of string representations of individual elements as
        **"value1,value2,value3"**

        :return: a string representation of the object.
        """
        result = ''

        for element in self:
            if len(result) > 0:
                result += ','
            result += StringConverter.to_string_with_default(element, '')

        return result

    def __str__(self):
        """
        Gets a string representation of the object.
        The result is a comma-separated list of string representations of individual elements as
        **"value1,value2,value3"**

        :return: a string representation of the object.
        """
        result = ''

        for element in self:
            if len(result) > 0:
                result += ','
            result += StringConverter.to_string_with_default(element, '')

        return result

    @staticmethod
    def from_values(*values: Any) -> 'AnyValueArray':
        """
        Creates a new :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>` from a list of values

        :param values: a list of values to initialize the created :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>`

        :return: a newly created :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>`.
        """
        return AnyValueArray(values)

    @staticmethod
    def from_value(value: Any) -> 'AnyValueArray':
        """
        Converts specified args into :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>`.

        :param value: args to be converted

        :return: a newly created :class:`AnyValueArray <pip_services3_commons.data.AnyValueArray.AnyValueArray>`.
        """
        value = ArrayConverter.to_nullable_array(value)
        if not (value is None):
            return AnyValueArray(value)
        return AnyValueArray()

    @staticmethod
    def from_string(values: str, separator: str, remove_duplicates: bool = False) -> 'AnyValueArray':
        """
        Splits specified string into elements using a separator and assigns
        the elements to a newly created AnyValueArray.

        :param values: a string args to be split and assigned to AnyValueArray

        :param separator: a separator to split the string

        :param remove_duplicates: (optional) true to remove duplicated elements

        :return: a newly created AnyValueArray.
        """
        result = AnyValueArray()

        if values is None or len(values) == 0:
            return result

        items = str(values).split(separator)
        for item in items:
            if (item is not None and len(item) > 0) or remove_duplicates is False:
                result.append(item)

        return result
