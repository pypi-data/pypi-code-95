# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.PropertiesComparisonRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Properties comparison rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from pip_services3_commons.validate import Schema
from .IValidationRule import IValidationRule
from .ObjectComparator import ObjectComparator
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType
from ..reflect.ObjectReader import ObjectReader


class PropertiesComparisonRule(IValidationRule):
    """
    Validation rule that compares two object properties.

    Example:

    .. code-block:: python

        schema = ObjectSchema().with_rule(PropertyComparisonRule("field1", "NE", "field2"))

        schema.validate({ field1: 1, field2: 2 })       # Result: no errors
        schema.validate({ field1: 1, field2: 1 })       # Result: field1 shall not be equal to field2
        schema.validate({})                             # Result: no errors
    """

    def __init__(self, property1: str, operation: str, property2: str):
        """
        Creates a new validation rule and sets its arguments.

        :param property1: a name of the first property to compare.

        :param operation: a comparison operation: "==" ("=", "EQ"), "!= " ("<>", "NE");
                                                  "<"/">" ("LT"/"GT"), "<="/">=" ("LE"/"GE"); "LIKE".

        :param property2: a name of the second property to compare.
        """
        self.__property1: str = property1
        self.__operation: str = operation
        self.__property2: str = property2

    def validate(self, path: str, schema: Schema, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        name = path or "args"
        value1 = ObjectReader.get_property(value, self.__property1)
        value2 = ObjectReader.get_property(value, self.__property2)

        if not ObjectComparator.compare(value1, self.__operation, value2):
            results.append(
                ValidationResult(
                    path,
                    ValidationResultType.Error,
                    "PROPERTIES_NOT_MATCH",
                    name + " must have " + str(self.__property1) + " " + str(self.__operation) + " " + str(
                        self.__property2),
                    value2,
                    value1
                )
            )
