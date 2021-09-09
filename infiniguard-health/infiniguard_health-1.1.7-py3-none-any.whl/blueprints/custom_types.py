import arrow
import numbers
from arrow.parser import ParserError
from represent import ReprHelper
from schematics.exceptions import ConversionError
from schematics.models import Model
from schematics.types import BaseType, BooleanType
from enum import Enum


# Copied (almost) verbatim from schamatics, v2.1.0
# https://github.com/schematics/schematics/blob/master/schematics/contrib/enum_type.py
class EnumType(BaseType):
    """A field type allowing to use native enums as values.
    Restricts values to enum members and (optionally) enum values.
    `use_values` - if set to True allows do assign enumerated values to the field.
    >> import enum
    >> class E(enum.Enum):
    ...    A = 1
    ...    B = 2
    >> from schematics import Model
    >> class AModel(Model):
    ...    foo = EnumType(E)
    >> a = AModel()
    >> a.foo = E.A
    >> a.foo.value == 1
    """
    MESSAGES = {
        'convert': "Couldn't interpret '{0}' as member of {1}."
    }

    def __init__(self, enum, use_values=False, **kwargs):
        """
        :param enum: Enum class to which restrict values assigned to the field.
        :param use_values: If true, also values of the enum (right-hand side) can be assigned here.
        Other args are passed to superclass.
        """
        self._enum_class = enum
        self._use_values = use_values
        super(EnumType, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        if isinstance(value, self._enum_class):
            return value
        else:
            by_name = self._find_by_name(value)
            if by_name:
                return by_name
            by_value = self._find_by_value(value)
            if by_value:
                return by_value
        raise ConversionError(self.messages['convert'].format(value, self._enum_class))

    def _find_by_name(self, value):
        if isinstance(value, str):
            try:
                return self._enum_class[value]
            except KeyError:
                pass

    def _find_by_value(self, value):
        if not self._use_values:
            return
        for member in self._enum_class:
            if member.value == value:
                return member

    def to_primitive(self, value, context=None):
        if isinstance(value, Enum):
            if self._use_values:
                return value.value
            else:
                return value.name
        else:
            return str(value)


class DataModel(Model):
    class Options(object):
        serialize_when_none = True

    @property
    def to_dict(self):
        return self._data

    def __repr__(self):
        r = ReprHelper(self)
        for key, value in self.to_primitive().items():
            r.keyword_with_value(key, value)
        return str(r)


class CustomBooleanType(BooleanType):
    """
    Boolean that serializes to custom values.
    * to_native receives different types of primitive strings that can can be converted to boolean
    ('yes', 'no', 'up', 'off', etc) and holds them as a Boolean.
    The boolean will be True if conforms to TRUE_VALUES and False otherwise. (In order to account for unknown values)

    * to_primitive converts the native boolean to string. This parent class converts it to 'True' or 'False'
    Sub classes are expected override the BOOL_TO_PRIMITIVE dict and return different strings.
    Possible contexts are 'true_false', 'yes_no', 'on_off', and 'up_down'.
    """

    # Overriding BooleanType class variables to extend acceptable values.
    TRUE_VALUES = ('true', '1', 'yes', 'on', 'up', 'active')
    BOOL_TO_PRIMITIVE = {True: 'True', False: 'False'}

    def to_native(self, value, context=None):
        if isinstance(value, str):
            return value.lower() in self.TRUE_VALUES

        return super().to_native(value, context)

    def to_primitive(self, value, context=None):
        if not isinstance(value, bool):
            raise ConversionError("Value to convert to primitive must be a Boolean.")

        return self.BOOL_TO_PRIMITIVE[value]


class YesNoType(CustomBooleanType):
    """
    Custom boolean types that serializes to YES/NO.
    """
    BOOL_TO_PRIMITIVE = {True: 'YES', False: 'NO'}


class UpDownType(CustomBooleanType):
    """
    Custom boolean types that serializes to UP/DOWN.
    """
    BOOL_TO_PRIMITIVE = {True: 'UP', False: 'DOWN'}


class OnOffType(CustomBooleanType):
    """
    Custom boolean types that serializes to ON/OFF.
    """
    BOOL_TO_PRIMITIVE = {True: 'ON', False: 'OFF'}


class ActiveInactiveType(CustomBooleanType):
    """
    Custom boolean types that serializes to ON/OFF.
    """
    BOOL_TO_PRIMITIVE = {True: 'active', False: 'inactive'}


class ArrowType(BaseType):
    MESSAGES = {'parse': u'Could not parse date {}.'}
    DATE_FORMAT = 'YYYY-MM-DDTHH:mm:ss UTC'

    def to_native(self, value, context=None):
        try:
            try:
                arrow_object = arrow.get(value)
            except ParserError:
                arrow_object = arrow.get(value, self.DATE_FORMAT)

        except (ValueError, TypeError, ParserError):
            raise ConversionError(self.MESSAGES['parse'].format(value))

        return arrow_object

    def to_primitive(self, value, context=None):
        if context == 'humanize':
            return value.humanize()
        else:
            return value.to('UTC').format(self.DATE_FORMAT)


class PercentageFloatToStringType(BaseType):
    """
    This type is used to represent the a float percentage (e.g .4) as a string for the user (e.g '40%').
    After receiving a float between 0 and 1, it is saved as a string (rounding to the closest integer).

    Since this is always what is displayed to the user, both native and primitive return this string.
    """
    def to_native(self, value, context=None):
        if isinstance(value, numbers.Number):
            percentage = int(round(value * 100))
            return str(percentage) + '%'

        return super().to_native(value, context)

    def to_primitive(self, value, context=None):
        """
        """
        return self.to_native(value, context)
