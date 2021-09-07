# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.PropertySchema
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Validation schema for object properties

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any

from pip_services3_commons.validate import IValidationRule, ValidationResult
from .Schema import Schema


class PropertySchema(Schema):
    """
    Schema to validate object properties

    Example:

    .. code-block:: python

        schema = ObjectSchema().with_property(PropertySchema("id", TypeCode.String))

        schema.validate({ id: "1", name: "ABC" })       # Result: no errors
        schema.validate({ name: "ABC" })                # Result: no errors
        schema.validate({ id: 1, name: "ABC" })         # Result: id type mismatch
    """

    def __init__(self, name: str = None, value_type: Any = None, required: bool = None,
                 rules: List[IValidationRule] = None):
        """
        Creates a new validation schema and sets its values.

        :param name: (optional) a property name

        :param value_type: (optional) a property type
        """
        super(PropertySchema, self).__init__(required, rules)
        self.__name = name
        self.__type = value_type

    def get_name(self) -> str:
        """
        Gets the property name.

        :return: the property name.
        """
        return self.__name

    def set_name(self, value: str):
        """
        Sets the property name.

        :param value: a new property name.
        """
        self.__name = value

    def get_type(self) -> Any:
        """
        Gets the property type.

        :return: the property type.
        """
        return self.__type

    def set_type(self, value: Any):
        """
        Sets a new property type.
        The type can be defined as type, type name or :class:`TypeCode <from pip_services3_commons.convert.TypeCode.TypeCode>`

        :param value: a new property type.
        """
        self.__type = value

    def _perform_validation(self, path: str, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against the schema and configured validation __rules.

        :param path: a dot notation path to the args.

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        path = self.get_name() if path is None or len(path) == 0 else path + "." + self.get_name()

        super(PropertySchema, self)._perform_validation(path, value, results)

        super(PropertySchema, self)._perform_type_validation(path, self.get_type(), value, results)
