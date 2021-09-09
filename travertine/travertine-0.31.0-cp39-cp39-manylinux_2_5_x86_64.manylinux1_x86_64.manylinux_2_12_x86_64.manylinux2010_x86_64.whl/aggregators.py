#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import operator
from dataclasses import dataclass
from functools import reduce
from typing import Sequence

from .structs import LazyPriceResult
from .types import Demand, Environment, PriceResultType, Procedure, Result, Undefined


class BaseAggregator:  # pragma: no cover
    pass


class SimpleAggregator(BaseAggregator):  # pragma: no cover
    """An aggregator that does not requires other aggregators."""


@dataclass(init=False, unsafe_hash=True)
class SumAggregator(SimpleAggregator):
    "Aggregate by addition."

    start: Result

    __slots__ = ("start",)

    def __init__(self, start: Result = 0) -> None:
        self.start = start

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        result = sum((r.result for r in results), self.start)
        return LazyPriceResult(title, proc, result, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class MultAggregator(SimpleAggregator):
    "Aggregate by multiplication."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        result = reduce(operator.mul, (r.result for r in results), 1)
        return LazyPriceResult(title, proc, result, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class DivideAggregator(SimpleAggregator):
    "Aggregate by dividing the first result from the second."

    default: Result

    __slots__ = ("default",)

    def __init__(self, default: Result = Undefined) -> None:
        self.default = default

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        try:
            top = results[0].result
            bottom = results[1].result
            return LazyPriceResult(title, proc, top / bottom, demand, env, results)
        except (IndexError, ZeroDivisionError, OverflowError):
            return LazyPriceResult(title, proc, self.default, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class MaxAggregator(SimpleAggregator):
    "Aggregate taking the result with greatest value (max)."

    default: Result

    __slots__ = ("default",)

    def __init__(self, default: Result = Undefined) -> None:
        self.default = default

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        result = max((r.result for r in results), default=self.default)
        return LazyPriceResult(title, proc, result, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class MinAggregator(SimpleAggregator):
    """Aggregate taking the result with lowest value (min)."""

    default: Result

    __slots__ = ("default",)

    def __init__(self, default: Result = Undefined) -> None:
        self.default = default

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        result = min((r.result for r in results), default=self.default)
        return LazyPriceResult(title, proc, result, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class CountAggregator(SimpleAggregator):
    "Aggregate by counting the results."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        return LazyPriceResult(title, proc, len(results), demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class CountDefinedAggregator(SimpleAggregator):
    "Aggregate by counting the non-undefined results."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        result = sum(1 for r in results if not isinstance(r.result, type(Undefined)))
        return LazyPriceResult(title, proc, result, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class TakeFirstAggregator(SimpleAggregator):
    "Aggregate by the first result."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        try:
            return LazyPriceResult(title, proc, results[0].result, demand, env, results)
        except IndexError:
            return LazyPriceResult(title, proc, 0, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class TakeFirstDefinedAggregator(SimpleAggregator):
    "Aggregate by the first non-undefined result."

    default: Result

    __slots__ = ("default",)

    def __init__(self, default: Result = Undefined):
        self.default = default

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        it = (r for r in results if not isinstance(r.result, type(Undefined)))
        try:
            return LazyPriceResult(title, proc, next(it).result, demand, env, results)
        except StopIteration:  # pragma: no cover
            return LazyPriceResult(title, proc, self.default, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class TakeLastAggregator(SimpleAggregator):
    "Aggregate by taking the last result."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        try:
            return LazyPriceResult(title, proc, results[-1].result, demand, env, results)
        except IndexError:
            return LazyPriceResult(title, proc, 0, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class TakeLastDefinedAggregator(SimpleAggregator):
    "Aggregate by taking the last non-undefined result."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        from xotless.itertools import last

        it = (r.result for r in results if not isinstance(r.result, type(Undefined)))
        result = last(it, 0)
        return LazyPriceResult(title, proc, result, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class AverageAggregator(SimpleAggregator):
    "Averages the results."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        from statistics import mean

        all_results = list(r.result for r in results)
        if not results or any(r is Undefined for r in all_results):
            value = Undefined  # type: Result
        else:
            try:
                value = mean(r for r in all_results)  # type: ignore
            except ValueError:
                value = Undefined
        return LazyPriceResult(title, proc, value, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class ModeAggregator(SimpleAggregator):
    "The mode of the result."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        from statistics import mode

        all_results = list(r.result for r in results)
        if not results or any(r is Undefined for r in all_results):
            value = Undefined  # type: Result
        else:
            try:
                value = mode(r for r in all_results)
            except ValueError:
                value = Undefined
        return LazyPriceResult(title, proc, value, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class FirstTimesCountAggregator(SimpleAggregator):
    "Takes the first and multiplies for the count."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        try:
            first: Result = results[0].result
            count = len(results)
        except IndexError:
            count = 0
            first = Undefined
        return LazyPriceResult(title, proc, first * count, demand, env, results)


@dataclass(init=False, unsafe_hash=True)
class LastTimesCountAggregator(SimpleAggregator):
    "Takes the last and multiplies for the count."

    def __call__(
        self,
        results: Sequence[PriceResultType],
        title: str,
        demand: Demand,
        env: Environment,
        proc: Procedure = None,
    ) -> PriceResultType:
        try:
            last: Result = results[-1].result
            count = len(results)
        except IndexError:
            count = 0
            last = Undefined
        return LazyPriceResult(title, proc, last * count, demand, env, results)
