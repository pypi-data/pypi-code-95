# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.OrRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Or rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Tuple

from pip_services3_commons.validate import Schema, ValidationResult
from .IValidationRule import IValidationRule


class OrRule(IValidationRule):
    """
    Validation rule to combine __rules with OR logical operation.
    When one of __rules returns no errors, than this rule also returns no errors.
    When all __rules return errors, than the rule returns all errors.

    Example:
    
    .. code-block:: python

        schema = Schema().with_rule(OrRule(ValueComparisonRule("LT", 1), ValueComparisonRule("GT", 10)))

        schema.validate(0)          # Result: no error
        schema.validate(5)          # Result: 5 must be less than 1 or 5 must be more than 10
        schema.validate(20)         # Result: no error
    """

    def __init__(self, *rules: IValidationRule):
        """
        Creates a new validation rule and sets its values.

        :param rules: a list of __rules to join with OR operator
        """
        self.__rules: Tuple[IValidationRule] = rules

    def validate(self, path: str, schema: Schema, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        if self.__rules is None or len(self.__rules) == 0:
            return

        local_results = []

        for rule in self.__rules:
            results_count = len(local_results)
            rule.validate(path, schema, value, local_results)
            if results_count == len(local_results):
                return

        for result in local_results:
            results.append(result)
