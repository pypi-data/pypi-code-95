# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.AnyValue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    AnyValue implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from copy import deepcopy
from datetime import datetime
from typing import Optional, Any

from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import AnyValueArray, AnyValueMap
from pip_services3_commons.data.ICloneable import ICloneable
from ..convert.BooleanConverter import BooleanConverter
from ..convert.DateTimeConverter import DateTimeConverter
from ..convert.FloatConverter import FloatConverter
from ..convert.IntegerConverter import IntegerConverter
from ..convert.LongConverter import LongConverter
from ..convert.StringConverter import StringConverter
from ..convert.TypeConverter import TypeConverter




class AnyValue(ICloneable):
    """
    Cross-language implementation of dynamic object what can hold args of any type.
    The stored args can be converted to different types using variety of accessor methods.

    Example:

    .. code-block:: python
    
        value1 = AnyValue("123.456")

        value1.get_as_integer()   # Result: 123
        value1.get_as_string()    # Result: "123.456"
        value1.get_as_float()     # Result: 123.456
    """

    def __init__(self, value: Any = None):
        """
        Creates a new instance of the object and assigns its args.

        :param value: (optional) args to initialize this object.
        """
        self.value: Any

        if isinstance(value, AnyValue):
            self.value = value.value
        else:
            self.value = value

    def get_type_code(self) -> TypeCode:
        """
        Gets type code for the args stored in this object.

        :return: type code of the object args.
        """
        return TypeConverter.to_type_code(self.value)

    def get_as_object(self) -> Any:
        """
        Gets the args stored in this object without any conversions

        :return: the object args.
        """
        return self.value

    def set_as_object(self, value: Any):
        """
        Sets a new args for this object

        :param value: the new object args.
        """
        self.value = value

    def get_as_nullable_string(self) -> str:
        """
        Converts object args into a string or returns null if conversion is not possible.

        :return: string args or None if conversion is not supported.
        """
        return StringConverter.to_nullable_string(self.value)

    def get_as_string(self) -> str:
        """
        Converts object args into a string or returns "" if conversion is not possible.

        :return: string args or "" if conversion is not supported.
        """
        return StringConverter.to_string(self.value)

    def get_as_string_with_default(self, default_value: str) -> str:
        """
        Converts object args into a string or returns default args if conversion is not possible.

        :param default_value: the default args.

        :return: string args or default if conversion is not supported.
        """
        return StringConverter.to_string_with_default(self.value, default_value)

    def get_as_nullable_boolean(self) -> Optional[bool]:
        """
        Converts object args into a boolean or returns null if conversion is not possible.

        :return: boolean args or null if conversion is not supported.
        """
        return BooleanConverter.to_nullable_boolean(self.value)

    def get_as_boolean(self) -> bool:
        """
        Converts object args into a boolean or returns false if conversion is not possible.

        :return: string args or false if conversion is not supported.
        """
        return BooleanConverter.to_boolean(self.value)

    def get_as_boolean_with_default(self, default_value: bool) -> bool:
        """
        Converts object args into a boolean or returns default args if conversion is not possible.

        :param default_value: the default args.

        :return: boolean args or default if conversion is not supported.
        """
        return BooleanConverter.to_boolean_with_default(self.value, default_value)

    def get_as_nullable_integer(self) -> Optional[int]:
        """
        Converts object args into an integer or returns None if conversion is not possible.

        :return: integer args or None if conversion is not supported.
        """
        return IntegerConverter.to_nullable_integer(self.value)

    def get_as_integer(self) -> int:
        """
        Converts object args into an integer or returns 0 if conversion is not possible.

        :return: integer args or 0 if conversion is not supported.
        """
        return IntegerConverter.to_integer(self.value)

    def get_as_integer_with_default(self, default_value: int) -> int:
        """
        Converts object args into a integer or returns default args if conversion is not possible.

        :param default_value: the default args.

        :return: integer args or default if conversion is not supported.
        """
        return IntegerConverter.to_integer_with_default(self.value, default_value)

    def get_as_nullable_long(self) -> Optional[float]:
        return LongConverter.to_nullable_long(self.value)

    def get_as_long(self) -> float:
        return LongConverter.to_long(self.value)

    def get_as_long_with_default(self, default_value: float) -> float:
        return LongConverter.to_long_with_default(self.value, default_value)

    def get_as_nullable_float(self) -> Optional[float]:
        """
        Converts object args into a float or returns None if conversion is not possible.

        :return: float args or None if conversion is not supported.
        """
        return FloatConverter.to_nullable_float(self.value)

    def get_as_float(self) -> float:
        """
        Converts object args into a float or returns 0 if conversion is not possible.

        :return: float args or 0 if conversion is not supported.
        """
        return FloatConverter.to_float(self.value)

    def get_as_float_with_default(self, default_value: float) -> float:
        """
        Converts object args into a float or returns default args if conversion is not possible.

        :param default_value: the default args.

        :return: float args or default if conversion is not supported.
        """
        return FloatConverter.to_float_with_default(self.value, default_value)

    def get_as_nullable_datetime(self) -> Optional[datetime]:
        """
        Converts object args into a Date or returns None if conversion is not possible.

        :return: Date args or None if conversion is not supported.
        """
        return DateTimeConverter.to_nullable_datetime(self.value)

    def get_as_datetime(self) -> datetime:
        """
        Converts object args into a Date or returns current date if conversion is not possible.

        :return: Date args or current date if conversion is not supported.
        """
        return DateTimeConverter.to_datetime(self.value)

    def get_as_datetime_with_default(self, default_value: datetime) -> datetime:
        """
        Converts object args into a Date or returns default args if conversion is not possible.

        :param default_value: the default args.

        :return: Date args or default if conversion is not supported.
        """
        return DateTimeConverter.to_datetime_with_default(self.value, default_value)

    def get_as_nullable_type(self, value_type: TypeCode) -> Optional[Any]:
        """
        Converts object args into a args defined by specied typecode. If conversion is not possible it returns None.

        :param value_type: the TypeCode that defined the type of the result

        :return: args defined by the typecode or null if conversion is not supported.
        """
        return TypeConverter.to_nullable_type(value_type, self.value)

    def get_as_type(self, value_type: TypeCode) -> Any:
        """
        Converts object args into a args defined by specied typecode.
        If conversion is not possible it returns default args for the specified type.

        :param value_type: the TypeCode that defined the type of the result

        :return: args defined by the typecode or type default args if conversion is not supported.
        """
        return TypeConverter.to_type(value_type, self.value)

    def get_as_type_with_default(self, value_type: TypeCode, default_value: Any) -> Any:
        """
        Converts object args into a args defined by specied typecode.
        If conversion is not possible it returns default args.

        :param value_type: the TypeCode that defined the type of the result

        :param default_value: the default args

        :return: args defined by the typecode or type default args if conversion is not supported.
        """
        return TypeConverter.to_type_with_default(value_type, self.value, default_value)

    def get_as_array(self) -> AnyValueArray:
        """
        Converts object args into an AnyArray or returns empty AnyArray if conversion is not possible.

        :return: AnyArray args or empty AnyArray if conversion is not supported.
        """
        return AnyValueArray.from_value(self.value)

    def get_as_map(self) -> AnyValueMap:
        """
        Converts object args into AnyMap or returns empty AnyMap if conversion is not possible.

        :return: AnyMap args or empty AnyMap if conversion is not supported.
        """
        return AnyValueMap.from_value(self.value)

    def equals(self, other: Any) -> bool:
        """
        Compares this object args to specified specified args.
        When direct comparison gives negative results it tries to compare values as strings.

        :param other: the args to be compared with.

        :return: true when objects are equal and false otherwise.
        """
        if other is None and self.value is None:
            return True
        if other is None or self.value is None:
            return False

        if isinstance(other, AnyValue):
            other = other._value

        if other == self.value:
            return True

        str_value1 = StringConverter.to_string(self.value)
        str_value2 = StringConverter.to_string(other)

        if str_value1 is None or str_value2 is None:
            return False

        return str_value1 == str_value2

    def __eq__(self, other):
        """
        Compares this object args to specified specified args.
        When direct comparison gives negative results it tries to compare values as strings.

        :param other: the args to be compared with.

        :return: true when objects are equal and false otherwise.
        """
        if other is None and self.value is None:
            return True
        if other is None or self.value is None:
            return False

        if isinstance(other, AnyValue):
            other = other._value

        if other == self.value:
            return True

        str_value1 = StringConverter.to_string(self.value)
        str_value2 = StringConverter.to_string(other)

        if str_value1 is None or str_value2 is None:
            return False

        return str_value1 == str_value2

    def __ne__(self, other):
        return not self.__eq__(other)

    def equals_as_type(self, value_type: TypeCode, obj: Any) -> bool:
        """
        Compares this object args to specified specified args.
        When direct comparison gives negative results it converts
        values to type specified by type code and compare them again.

        :param value_type: the Typecode type that defined the type of the result

        :param obj: the args to be compared with.

        :return: true when objects are equal and false otherwise.
        """
        if obj is None and self.value is None:
            return True
        if obj is None or self.value is None:
            return False

        if isinstance(obj, AnyValue):
            obj = obj._value

        if obj == self.value:
            return True

        value1 = TypeConverter.to_type(value_type, self.value)
        value2 = TypeConverter.to_type(value_type, obj)

        if value1 is None or value2 is None:
            return False

        return value1 == value2

    def __str__(self):
        """
        Gets a string representation of the object.

        :return: a string representation of the object.
        """
        return StringConverter.to_string(self.value)

    def to_string(self) -> str:
        """
        Gets a string representation of the object.

        :return: a string representation of the object.
        """
        return StringConverter.to_string(self.value)

    def clone(self) -> Any:
        """
        Creates a binary clone of this object.

        :return: a clone of this object.
        """
        return AnyValue(deepcopy(self.value))
