# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.ExcludedRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Excluded rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Tuple

from pip_services3_commons.validate import Schema, ObjectComparator
from .IValidationRule import IValidationRule
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType


class ExcludedRule(IValidationRule):
    """
    Validation rule to check that args is excluded from the list of constants.

    Example:

    .. code-block:: python
    
        schema = Schema().with_rule(ExcludedRule(1, 2, 3))

        schema.validate(2)      # Result: 2 must not be one of 1, 2, 3
        schema.validate(10)     # Result: no errors
    """

    def __init__(self, *values: Any):
        """
        Creates a new validation rule and sets its values.

        :param values: a list of constants that args must be excluded from
        """
        self.__values: Tuple[Any] = values

    def validate(self, path: str, schema: Schema, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        if not self.__values:
            return []

        name = path or "args"
        found = False

        for this_value in self.__values:
            if ObjectComparator.compare(value, 'EQ', this_value):
                found = True
                break

        if found:
            results.append(
                ValidationResult(
                    path,
                    ValidationResultType.Error,
                    "VALUE_INCLUDED",
                    name + " must not be one of " + str(self.__values),
                    self.__values,
                    None
                )
            )
