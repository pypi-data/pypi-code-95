# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.ArraySchema
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Array schema implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from typing import Any, List, Sequence

from pip_services3_commons.convert import TypeCode, TypeConverter
from pip_services3_commons.validate import IValidationRule
from .Schema import Schema
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType
from ..reflect.ObjectReader import ObjectReader


class ArraySchema(Schema):
    """
    Schema to validate arrays.

    Example:

    .. code-block:: python

        schema = ArraySchema(TypeCode.String)

        schema.validate(["A", "B", "C"])    # Result: no errors
        schema.validate([1, 2, 3])          # Result: element type mismatch
        schema.validate("A")                # Result: type mismatch
    """

    def __init__(self, value_type: Any = None, required: bool = None, rules: Sequence[IValidationRule] = None):
        """
        Creates a new instance of validation schema and sets its values.

        :param value_type: a type of array elements. None means that elements may have any type.
        :param required: (optional) true to always require non-null values.
        :param rules: (optional) a list with validation __rules.
        """
        super(ArraySchema, self).__init__(required, rules)
        self.__value_type: Any = value_type

    def get_value_type(self) -> Any:
        """
        Gets the type of array elements.
        Null means that elements may have any type.

        :return: the type of array elements.
        """
        return self.__value_type

    def set_value_type(self, value: Any):
        """
        Sets the type of array elements.
        Null means that elements may have any type.

        :param value: a type of array elements.
        """
        self.__value_type = value

    def _perform_validation(self, path: str, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against the schema and configured validation __rules.

        :param path: a dot notation path to the args.

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        name = path or "args"
        value = ObjectReader.get_value(value)

        super(ArraySchema, self)._perform_validation(path, value, results)

        if value is None:
            return

        if isinstance(value, (set, list, tuple)):
            index = 0
            for element in value:
                element_path = str(index) if path is None or len(path) == 0 else path + "." + str(index)
                self._perform_type_validation(element_path, self.get_value_type(), element, results)
                index += 1
        else:
            results.append(
                ValidationResult(
                    path,
                    ValidationResultType.Error,
                    "VALUE_ISNOT_ARRAY",
                    name + " type must be List or Array",
                    TypeCode.Array,
                    TypeConverter.to_type_code(value)
                )
            )
