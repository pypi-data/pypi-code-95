# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.AtLeastOneExistRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    At least one exist rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any, Tuple

from pip_services3_commons.validate import Schema
from .IValidationRule import IValidationRule
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType
from ..reflect.ObjectReader import ObjectReader


class AtLeastOneExistRule(IValidationRule):
    """
    Validation rule that check that at least one of the object properties is not None.

    Example:

    .. code-block:: python

        schema = Schema().with_rule(AtLeastOneExistsRule("field1", "field2"))
        schema.validate({ 'field1': 1, 'field2': "A" })     # Result: no errors
        schema.validate({ 'field1': 1 })                  # Result: no errors
        schema.validate({ })                            # Result: at least one of properties field1, field2 must exist
    """

    def __init__(self, *properties: str):
        """
        Creates a new validation rule and sets its values

        :param properties: a list of property names where at least one property must exist
        """
        self.__properties: Tuple[str] = properties

    def validate(self, path: str, schema: Schema, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        name = path or "args"
        found = []

        for prop in self.__properties:
            property_value = ObjectReader.get_property(value, prop)
            if \
                    property_value is not None:
                found.append(prop)

        if len(found) == 0:
            results.append(
                ValidationResult(
                    path,
                    ValidationResultType.Error,
                    "VALUE_NULL",
                    name + " must have at least one property from " + str(self.__properties),
                    self.__properties,
                    None
                )
            )
