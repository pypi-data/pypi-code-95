# -*- coding: utf-8 -*-
"""
    pip_services_common.validate.ValidationException
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Validation error type
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Optional

from pip_services3_commons.validate import ValidationResult
from .ValidationResultType import ValidationResultType
from ..errors.BadRequestException import BadRequestException


class ValidationException(BadRequestException):
    """
    Errors in schema validation.

    Validation errors are usually generated based in :class:`ValidationResult <pip_services3_commons.validate.ValidationResult.ValidationResult>`.
    If using strict mode, warnings will also raise validation exceptions.
    """

    def __init__(self, correlation_id: Optional[str], message: Optional[str], results: List[ValidationResult]):
        """
        Creates a new instance of validation error and assigns its values.

        :param correlation_id: (optional) a unique transaction id to trace execution through call chain.

        :param results: (optional) a list of validation results

        :param message: (optional) a human-readable description of the error.
        """
        super().__init__(correlation_id, 'INVALID_DATA',
                         ValidationException.compose_message(results) or message)

        if results:
            self.with_details('results', results)

    @staticmethod
    def compose_message(results: List[ValidationResult]) -> str:
        """
        Composes human readable error message based on validation results.

        :param results: a list of validation results.

        :return: a composed error message.
        """
        builder = 'Validation failed'

        if results and len(results) > 0:
            first = True
            for result in results:
                if result.get_type() == ValidationResultType.Information:
                    continue

                builder += ": " if first else ', '
                builder += result.get_message()
                first = False

        return builder

    @staticmethod
    def from_results(correlation_id: Optional[str], results: List[ValidationResult],
                     strict: bool) -> 'ValidationException':
        """
        Creates a new ValidationException based on errors in validation results.
        If validation results have no errors, than null is returned.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param results: list of validation results that may contain errors
        :param strict: true to treat warnings as errors.
        :return: a newly created ValidationException or null if no errors in found.
        """
        has_errors = False

        for i in range(len(results)):
            result = results[i]

            if result.get_type() == ValidationResultType.Error:
                has_errors = True

            if strict and result.get_type() == ValidationResultType.Warning:
                has_errors = True

        return ValidationException(correlation_id, None, results) if has_errors else None

    @staticmethod
    def throw_exception_if_needed(correlation_id: Optional[str], results: List[ValidationResult], strict: bool):
        """
        Throws ValidationException based on errors in validation results.
        If validation results have no errors, than no error is thrown.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param results: list of validation results that may contain errors

        :param strict: true to treat warnings as errors.
        """
        ex = ValidationException.from_results(correlation_id, results, strict)

        if ex:
            raise ex
