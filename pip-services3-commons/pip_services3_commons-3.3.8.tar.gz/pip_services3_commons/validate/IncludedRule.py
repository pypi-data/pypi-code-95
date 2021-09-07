# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.IncludedRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Included rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Sequence, Any, List, Tuple

from pip_services3_commons.validate import Schema, ObjectComparator
from .IValidationRule import IValidationRule
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType


class IncludedRule(IValidationRule):
    """
    Validation rule to check that args is included into the list of constants.

    Example:

    .. code-block:: python

        schema = new Schema().with_rule(IncludedRule(1, 2, 3))

        schema.validate(2)      # Result: no errors
        schema.validate(10)     # Result: 10 must be one of 1, 2, 3
    """

    def __init__(self, *values: Any):
        """
        Creates a new validation rule and sets its values.

        :param values: a list of constants that args must be included to
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

        if not found:
            results.append(
                ValidationResult(
                    path,
                    ValidationResultType.Error,
                    "VALUE_NOT_INCLUDED",
                    name + " must be one of " + str(self.__values),
                    self.__values,
                    None
                )
            )
