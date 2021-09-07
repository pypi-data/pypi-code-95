# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.IValidationRule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for schema validation __rules.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import List, Any

from pip_services3_commons.validate.ValidationResult import ValidationResult


class IValidationRule(ABC):
    """
    Interface for validation __rules.
    Validation rule can validate one or multiple values
    against complex __rules like: args is in range, one property is less than another property,
    enforce enumerated values and more.

    This interface allows to implement custom __rules.
    """

    def validate(self, path: str, schema: 'Schema', value: Any, results: List[ValidationResult]):
        """
        Validates a given args against this rule.

        :param path: a dot notation path to the args.

        :param schema: a schema this rule is called from

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        raise NotImplementedError('Method from interface definition')
