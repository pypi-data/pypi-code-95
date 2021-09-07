# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.ValueComparisonRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Value comparison rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from pip_services3_commons.validate import Schema
from .IValidationRule import IValidationRule
from .ObjectComparator import ObjectComparator
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType


class ValueComparisonRule(IValidationRule):
    """
    Validation rule that compares args to a constant.

    Example:

    .. code-block:: python
    
        schema = Schema().with_rule(ValueComparisonRule("EQ", 1))

        schema.validate(1)          # Result: no errors
        schema.validate(2)          # Result: 2 is not equal to 1
    """

    def __init__(self, operation: Any, value: Any):
        """
        Creates a new validation rule and sets its values.

        :param operation: a comparison operation: "==" ("=", "EQ"), "!= " ("<>", "NE");
                                                  "<"/">" ("LT"/"GT"), "<="/">=" ("LE"/"GE"); "LIKE".

        :param value: a constant args to compare to
        """
        self.__operation: Any = operation
        self.__value: Any = value

    def validate(self, path: str, schema: Schema, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        name = path if not (path is None) else "args"

        if not ObjectComparator.compare(value, self.__operation, self.__value):
            results.append(
                ValidationResult(
                    path,
                    ValidationResultType.Error,
                    "BAD_VALUE",
                    name + " must " + str(self.__operation) + " " + str(self.__value) + " but found " + str(value),
                    str(self.__operation) + " " + str(self.__value),
                    str(value)
                )
            )
