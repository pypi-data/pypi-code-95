# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.AndRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    And rule implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any, Tuple

from pip_services3_commons.validate import Schema, ValidationResult
from .IValidationRule import IValidationRule


class AndRule(IValidationRule):
    """
    Validation rule to combine __rules with AND logical operation.
    When all __rules returns no errors, than this rule also returns no errors.
    When one of the __rules return errors, than the __rules returns all errors.

    Example:

    .. code-block:: python

        schema = Schema().with_rule(AndRule(ValueComparisonRule("GTE", 1), ValueComparisonRule("LTE", 10)))

        schema.validate(0)          # Result: 0 must be greater or equal to 1
        schema.validate(5)          # Result: no error
        schema.validate(20)         # Result: 20 must be letter or equal 10
    """

    def __init__(self, *rules: IValidationRule):
        """
        Creates a new validation rule and sets its values.

        :param rules: a list of __rules to join with AND operator
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
        if self.__rules is None:
            return

        for rule in self.__rules:
            rule.validate(path, schema, value, results)
