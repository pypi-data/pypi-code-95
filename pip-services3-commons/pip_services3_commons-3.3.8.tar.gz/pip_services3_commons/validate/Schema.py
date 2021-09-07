# -*- coding: utf-8 -*-
"""
    pip_services3_commons.validate.Schema
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Validation schema for complex objects.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Any, Optional

from pip_services3_commons.convert import TypeCode
from pip_services3_commons.validate.IValidationRule import IValidationRule
from .ValidationException import ValidationException
from .ValidationResult import ValidationResult
from .ValidationResultType import ValidationResultType
from ..convert.TypeConverter import TypeConverter
from ..reflect.ObjectReader import ObjectReader
from ..reflect.TypeMatcher import TypeMatcher


class Schema:
    """
    Basic schema that validates values against a set of validation __rules.

    This schema is used as a basis for specific schemas to validate
    objects, project properties, arrays and maps.
    """

    def __init__(self, required: bool = False, rules: List[IValidationRule] = None):
        """
        Creates a new instance of validation schema and sets its values.

        :param required: (optional) true to always require non-null values.

        :param rules: (optional) a list with validation __rules.
        """
        self.__required: bool = required
        self.__rules: List[IValidationRule] = rules or []

    def is_required(self) -> bool:
        """
        Gets a flag that always requires non-null values.
        For null values it raises a validation error.

        :return: true to always require non-null values and false to allow null values.
        """
        return self.__required

    def set_required(self, value: bool):
        """
        Sets a flag that always requires non-null values.

        :param value: true to always require non-null values and false to allow null values.
        """
        self.__required = value

    def get_rules(self) -> List[IValidationRule]:
        """
        Gets validation __rules to check values against.

        :return: a list with validation __rules.
        """
        return self.__rules

    def set_rules(self, value: List[IValidationRule]):
        """
        Sets validation __rules to check values against.

        :param value: a list with validation __rules.
        """
        self.__rules = value

    def make_required(self) -> 'Schema':
        """
        Makes validated values always __required (non-null).
        For null values the schema will raise errors.

        This method returns reference to this error to implement Builder pattern
        to chain additional calls.

        :return: this validation schema
        """
        self.__required = True
        return self

    def make_optional(self) -> 'Schema':
        """
        Makes validated values optional.
        Validation for null values will be skipped.

        This method returns reference to this error to implement Builder pattern
        to chain additional calls.

        :return: this validation schema
        """
        self.__required = False
        return self

    def with_rule(self, rule: IValidationRule) -> 'Schema':
        """
        Adds validation rule to this schema.

        This method returns reference to this error to implement Builder pattern
        to chain additional calls.

        :param rule: a validation rule to be added.

        :return: this validation schema.
        """
        self.__rules = self.__rules or []
        self.__rules.append(rule)
        return self

    def _perform_validation(self, path: str, value: Any, results: List[ValidationResult]):
        """
        Validates a given args against the schema and configured validation __rules.

        :param path: a dot notation path to the args.

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        name = path or "args"

        if value is None:
            # Check for __required values
            if self.is_required():
                results.append(
                    ValidationResult(
                        path,
                        ValidationResultType.Error,
                        "VALUE_IS_NULL",
                        name + " must not be null",
                        "NOT NULL",
                        None
                    )
                )
        else:
            value = ObjectReader.get_value(value)

            # Check validation __rules
            if self.__rules is not None:
                for rule in self.__rules:
                    rule.validate(path, self, value, results)

    def __type_to_string(self, typ: Any) -> str:
        if typ is None:
            return "unknown"
        if isinstance(typ, TypeCode):
            return TypeConverter.to_string(typ)
        return str(typ)

    def _perform_type_validation(self, path: str, typ: Any, value: Any, results: List[ValidationResult]):
        """
        Validates a given args to match specified type.
        The type can be defined as a Schema, type, a type name or :class:`TypeCode <pip_services3_commons.convert.TypeCode.TypeCode>`.
        When type is a Schema, it executes validation recursively against that Schema.

        :param path: a dot notation path to the args.

        :param typ: a type to match the args type

        :param value: a args to be validated.

        :param results: a list with validation results to add new results.
        """
        # If type it not defined then skip
        if typ is None:
            return

        # Perform validation against schema
        if isinstance(typ, Schema):
            schema = typ
            schema._perform_validation(path, value, results)
            return

        # If args is null then skip
        value = ObjectReader.get_value(value)
        if value is None:
            return

        name = path or "args"
        value_type = TypeConverter.to_type_code(value)

        # Match types
        if TypeMatcher.match_type(typ, value_type, value):
            return

        # Generate type mismatch error
        results.append(
            ValidationResult(
                path,
                ValidationResultType.Error,
                "TYPE_MISMATCH",
                name + " type must be " +
                self.__type_to_string(typ) + " but found " +
                self.__type_to_string(value_type),
                typ,
                value_type
            )
        )

    def validate(self, value: Any) -> List[ValidationResult]:
        """
        Validates the given args and results validation results.

        :param value: a args to be validated.

        :return: a list with validation results.
        """
        results = []
        self._perform_validation("", value, results)
        return results

    def validate_and_return_exception(self, correlation_id: Optional[str], value: Any,
                                      strict: bool = False) -> ValidationException:
        """
        Validates the given args and returns a :class:`ValidationException <pip_services3_commons.validate.ValidationException.ValidationException>` if errors were found.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param value: a args to be validated.
        :param strict: true to treat warnings as errors.
        """
        results = self.validate(value)
        return ValidationException.from_results(correlation_id, results, strict)

    def validate_and_throw_exception(self, correlation_id: Optional[str], value: Any, strict: bool = False):
        """
        Validates the given args and throws a :class:`ValidationException <pip_services3_commons.validate.ValidationException.ValidationException>` if errors were found.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param value: a args to be validated.

        :param strict: true to treat warnings as errors.
        """
        results = self.validate(value)
        ValidationException.throw_exception_if_needed(correlation_id, results, strict)
