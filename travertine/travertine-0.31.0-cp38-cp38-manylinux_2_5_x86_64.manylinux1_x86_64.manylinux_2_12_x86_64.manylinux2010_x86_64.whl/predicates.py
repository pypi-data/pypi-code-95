#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from dataclasses import dataclass
from datetime import date, datetime

from xotl.tools.infinity import InfinityType
from xotless.domains import EquivalenceSet, IntervalSet, Range

from .i18n import _
from .structs import _convert_to_runtime_value
from .types import (
    AVM,
    MATCH,
    NO_KIND,
    RANGE,
    AttributeLocator,
    EqTypeClass,
    OrdTypeClass,
    PredicateKind,
    TypedAttribute,
)


class BasePredicate:  # pragma: no cover
    def get_kind(self) -> PredicateKind:
        return NO_KIND


class SimplePredicate(BasePredicate):  # pragma: no cover
    pass


# Since MR !1397 predicates are highly coupled with BranchingProcedure and
# BacktrackingBrachingProcedure.  So predicates are not executed directly and
# are divided into two kinds of predicates:
#
# - range predicates
# - equality predicates
#
# Predicate 'Otherwise' is treated specially by branching procedures.  We'll
# keep the old implementation of __call__ until we can be sure all procedures
# are always well-typed.
#


@dataclass(init=False, unsafe_hash=True)
class Otherwise(BasePredicate):
    "Always True."

    @property
    def avm(self) -> AVM:
        return {}


@dataclass(init=False, unsafe_hash=True)
class ValidityPredicate(SimplePredicate):
    "The demand date is in a given period."

    # For a demand to match this predicate, its date must be at or after the
    # given `start` date and before the given `end` date.

    period: Range[datetime]

    __slots__ = ("period",)

    def __init__(self, start: datetime, end: datetime) -> None:
        assert (
            start is None or start is False or isinstance(start, (date, InfinityType))
        ), f"Invalid {start!r}"
        assert (
            end is None or end is False or isinstance(end, (date, InfinityType))
        ), f"Invalid {end!r}"
        self.period = Range.new_open_right(start, end)

    def __str__(self):
        return _("Demand date since {start} and before {end}").format(
            start=self.period.lowerbound, end=self.period.upperbound
        )

    def __repr__(self):
        return (
            f"ValidityPredicate({self.period.lowerbound!r}, {self.period.upperbound!r})"
        )

    def get_args(self):
        lower, upper = self.period
        return _convert_to_runtime_value(lower), _convert_to_runtime_value(upper)

    @property
    def avm(self) -> AVM:
        return {self.get_attr_locator(): (IntervalSet([self.period]),)}

    def get_attr_locator(self) -> AttributeLocator:
        return AttributeLocator.of_demand(self.get_internal_attr())

    def get_internal_attr(self) -> TypedAttribute:
        return TypedAttribute.from_typed_name(
            "date", datetime, display_name="Validity date"
        )

    def get_kind(self) -> PredicateKind:
        return PredicateKind(RANGE.from_range(self.period), self.get_attr_locator())


@dataclass(init=False, unsafe_hash=True)
class ExecutionPredicate(SimplePredicate):
    "The commodity execution date is in a given period."

    # For a demand to match this predicate, all of its commodities' start
    # date must be at or after the given `start` date and before the given
    # `end` date.

    season: Range[datetime]

    __slots__ = ("season",)

    def __init__(self, start: datetime, end: datetime) -> None:
        assert (
            start is None or start is False or isinstance(start, (date, InfinityType))
        ), f"Invalid {start!r}"
        assert (
            end is None or end is False or isinstance(end, (date, InfinityType))
        ), f"Invalid {end!r}"
        self.season = Range.new_open_right(start, end)

    def __str__(self):
        return _("Execution date since {start} and before {end}").format(
            start=self.season.lowerbound, end=self.season.upperbound
        )

    def __repr__(self):
        return (
            f"ExecutionPredicate({self.season.lowerbound!r}, {self.season.upperbound!r})"
        )

    def get_args(self):
        lower, upper = self.season
        return _convert_to_runtime_value(lower), _convert_to_runtime_value(upper)

    @property
    def avm(self) -> AVM:
        return {self.get_attr_locator(): (IntervalSet([self.season]),)}

    def get_attr_locator(self) -> AttributeLocator:
        return AttributeLocator.of_commodity(self.get_internal_attr())

    def get_internal_attr(self) -> TypedAttribute:
        return TypedAttribute.from_typed_name(
            "start_date", datetime, display_name="Execution date"
        )

    def get_kind(self) -> PredicateKind:
        return PredicateKind(RANGE.from_range(self.season), self.get_attr_locator())


@dataclass(init=False, unsafe_hash=True)
class MatchesAttributePredicate(SimplePredicate):
    "The commodities have a given attribute set to a given value."

    attr: TypedAttribute
    value: EqTypeClass

    __slots__ = ("attr", "value")

    def __init__(self, attr: TypedAttribute, value: EqTypeClass) -> None:
        self.attr = attr
        self.value = value

    def __str__(self):
        return _("Attribute '{attr.name}' has value {value}").format(
            attr=self.attr, value=self.value
        )

    def get_args(self):
        return self.attr.name, _convert_to_runtime_value(self.value)

    @property
    def avm(self) -> AVM:
        return {self.get_attr_locator(): (EquivalenceSet({self.value}),)}

    def get_attr_locator(self) -> AttributeLocator:
        return AttributeLocator.of_commodity(self.get_internal_attr())

    def get_internal_attr(self) -> TypedAttribute:
        return self.attr

    def get_kind(self) -> PredicateKind:
        return PredicateKind(MATCH(self.value), self.get_attr_locator())


@dataclass(init=False, unsafe_hash=True)
class AttributeInRangePredicate(SimplePredicate):
    "The commodities have a given attribute in a given range."

    attr: TypedAttribute
    lowerbound: OrdTypeClass
    upperbound: OrdTypeClass

    __slots__ = ("attr", "lowerbound", "upperbound")

    def __init__(
        self, attr: TypedAttribute, lowerbound: OrdTypeClass, upperbound: OrdTypeClass
    ) -> None:
        self.attr = attr
        self.lowerbound = lowerbound
        self.upperbound = upperbound

    @property
    def range(self):
        return Range.new_open_right(self.lowerbound, self.upperbound)

    def __str__(self):
        return _("Attribute '{attr.name}' is in the range of {range}").format(
            attr=self.attr, range=self.range
        )

    def get_typed_attribute(self):
        return self.attr

    def get_args(self):
        return (
            self.attr.name,
            _convert_to_runtime_value(self.lowerbound),
            _convert_to_runtime_value(self.upperbound),
        )

    @property
    def avm(self) -> AVM:
        return {self.get_attr_locator(): (IntervalSet([self.range]),)}

    def get_attr_locator(self) -> AttributeLocator:
        return AttributeLocator.of_commodity(self.get_internal_attr())

    def get_internal_attr(self) -> TypedAttribute:
        return self.attr

    def get_kind(self) -> PredicateKind:
        return PredicateKind(
            RANGE(self.lowerbound, self.upperbound), self.get_attr_locator()
        )


@dataclass(init=False, unsafe_hash=True)
class QuantityPredicate(SimplePredicate):
    "The requested quantity is within given bounds."

    # A demand matches this predicate if all its requests have a quantities
    # greater or equal to 'least', and lesser than 'most'.
    #
    # If `lower` is not given (left blank), no lower limit is tested.
    # If `upper` is left blank, no upper limit is tested.

    range: Range  # IMPORTANT: without this all instances of QuantityPredicate compare equal.

    __slots__ = ("range",)

    def __init__(self, lower: float = None, upper: float = None) -> None:
        self.range = Range.new_open_right(lower, upper)

    def __repr__(self):
        return f"QuantityPredicate({self.range.lowerbound!r}, {self.range.upperbound!r})"

    def __str__(self):
        return _(
            "Quantity is greater or equal to {min} and less that {upperbound}"
        ).format(min=self.range.lowerbound, upperbound=self.range.upperbound)

    def get_args(self):
        lower, upper = self.range
        return _convert_to_runtime_value(lower), _convert_to_runtime_value(upper)

    @property
    def avm(self) -> AVM:
        return {self.get_attr_locator(): (IntervalSet([self.range]),)}

    def get_attr_locator(self) -> AttributeLocator:
        return AttributeLocator.of_request(self.get_internal_attr())

    def get_internal_attr(self) -> TypedAttribute:
        return TypedAttribute.from_typed_name("quantity", float, display_name="Quantity")

    def get_kind(self) -> PredicateKind:
        return PredicateKind(RANGE.from_range(self.range), self.get_attr_locator())
