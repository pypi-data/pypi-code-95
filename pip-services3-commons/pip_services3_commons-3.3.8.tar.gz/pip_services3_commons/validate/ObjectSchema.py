# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.ObjectSchema
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Object schema implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any, Optional

from pip_services3_commons.validate import IValidationRule, ObjectComparator
from .PropertySchema import PropertySchema
from .Schema import Schema
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType
from ..reflect.ObjectReader import ObjectReader


class ObjectSchema(Schema):
    """
    Schema to validate user defined objects.

    Example:

    .. code-block:: python

        schema = ObjectSchema(false)
                            .with_optional_property("id", TypeCode.String)
                            .with_required_property("name", TypeCode.String)

        schema.validate({ id: "1", name: "ABC" })       // Result: no errors
        schema.validate({ name: "ABC" })                // Result: no errors
        schema.validate({ id: 1, name: "ABC" })         // Result: id type mismatch
        schema.validate({ id: 1, __name: "ABC" })        // Result: name is missing, unexpected __name
        schema.validate("ABC")                          // Result: type mismatch
    """

    def __init__(self, allow_undefined: bool = False, required: bool = None, rules: List[IValidationRule] = None):
        """
        Creates a new validation schema and sets its values.

        :param allow_undefined: true to allow properties undefines in the schema
        :param required: (optional) true to always require non-null values.
        :param rules: (optional) a list with validation __rules.
        """
        super(ObjectSchema, self).__init__(required, rules)
        self.__allow_undefined: bool = allow_undefined
        self.__properties: List[PropertySchema] = []

    def get_properties(self) -> List[PropertySchema]:
        """
        Gets validation schemas for object properties.

        :return: the list of property validation schemas.
        """
        return self.__properties

    def set_properties(self, value: List[PropertySchema]):
        """
        Sets validation schemas for object properties.

        :param value: a list of property validation schemas.
        """
        self.__properties = value

    @property
    def is_undefined_allowed(self) -> bool:
        """
        Gets flag to allow undefined properties

        :return:true to allow undefined properties and false to disallow.
        """
        return self.__allow_undefined

    @is_undefined_allowed.setter
    def is_undefined_allowed(self, value: bool):
        """
        Sets flag to allow undefined properties

        :param value: true to allow undefined properties and false to disallow.
        """
        self.__allow_undefined = value

    def allow_undefined(self, value: bool) -> 'ObjectSchema':
        """
        Sets flag to allow undefined properties

        This method returns reference to this error to implement Builder pattern
        to chain additional calls.

        :param value: true to allow undefined properties and false to disallow.

        :return: this validation schema.
        """
        self.__allow_undefined = value
        return self

    def with_property(self, schema: PropertySchema) -> 'ObjectSchema':
        """
        Adds a validation schema for an object property.

        This method returns reference to this error to implement Builder pattern
        to chain additional calls.

        :param schema: a property validation schema to be added.

        :return: this validation schema.
        """
        self.__properties.append(schema)
        return self

    def with_required_property(self, name: str, typ: Optional[Any] = None, *rules: IValidationRule) -> 'ObjectSchema':
        """
        Adds a validation schema for a __required object property.

        :param name: a property name.

        :param typ: (optional) a property schema or type.

        :param rules: (optional) a list of property validation __rules.

        :return: the validation schema
        """
        schema = PropertySchema(name, typ)
        schema.set_rules(list(rules[:]))
        schema.make_required()
        return self.with_property(schema)

    def with_optional_property(self, name: str, typ: Optional[Any] = None, *rules: IValidationRule) -> 'ObjectSchema':
        """
        Adds a validation schema for an optional object property.

        :param name: a property name.

        :param typ: (optional) a property schema or type.

        :param rules: (optional) a list of property validation __rules.

        :return: the validation schema
        """
        schema = PropertySchema(name, typ)
        schema.set_rules(list(rules[:]))
        schema.make_optional()
        return self.with_property(schema)

    def _perform_validation(self, path: str, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against the schema and configured validation __rules.

        :param path: a dot notation path to the args.

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        super(ObjectSchema, self)._perform_validation(path, value, results)

        if value is None:
            return

        name = path or "args"
        properties = ObjectReader.get_properties(value)

        # Process defined properties
        if self.__properties is not None:
            for property_schema in self.__properties:
                processed_name = None

                for (key, value) in properties.items():

                    # Find properties case insensitive
                    if ObjectComparator.are_equal(property_schema.get_name(), key):
                        property_schema._perform_validation(path, value, results)
                        processed_name = key#private_obj_name + key
                        break

                if processed_name is None:
                    property_schema._perform_validation(path, None, results)
                else:
                    del properties[processed_name]

        # Process unexpected properties
        if not self.__allow_undefined:
            for (key, value) in properties.items():
                property_path = key if path is None or len(path) == 0 else path + "." + key

                results.append(
                    ValidationResult(
                        property_path,
                        ValidationResultType.Warning,
                        "UNEXPECTED_PROPERTY",
                        name + " contains unexpected property " + str(key),
                        None,
                        key
                    )
                )
