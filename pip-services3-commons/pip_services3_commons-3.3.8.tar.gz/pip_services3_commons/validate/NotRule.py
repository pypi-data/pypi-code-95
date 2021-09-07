# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.NotRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Not rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from pip_services3_commons.validate import Schema
from .IValidationRule import IValidationRule
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType


class NotRule(IValidationRule):
    """
    Validation rule negate another rule.
    When embedded rule returns no errors, than this rule return an error.
    When embedded rule return errors, than the rule returns no errors.

    Example:

    .. code-block:: python
    
        schema = Schema().with_rule(NotRule(ValueComparisonRule("EQ", 1)))

        schema.validate(1)          # Result: error
        schema.validate(5)          # Result: no error
    """

    def __init__(self, rule: IValidationRule):
        """
        Creates a new validation rule and sets its values

        :param rule: a rule to be negated.
        """
        self.__rule: IValidationRule = rule

    def validate(self, path: str, schema: Schema, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        if not self.__rule:
            return

        name = path or "args"
        local_results: List[ValidationResult] = []

        self.__rule.validate(path, schema, value, local_results)

        if len(local_results) > 0:
            return

        results.append(ValidationResult(
            path,
            ValidationResultType.Error,
            'NOT_FAILED',
            'Negative check for ' + name + ' failed',
            None,
            None
        ))
