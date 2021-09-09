#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import unittest
from functools import partial

import immutables
from hypothesis import strategies
from travertine.structs import Demand, PriceResult
from travertine.types import Environment, PriceResultType, Undefined

prices = strategies.integers(min_value=1, max_value=10 ** 12)
maybe_prices = prices | strategies.just(Undefined)


class PriceCaseMixin:
    def assertPriceMatches(self, result, expected, places=None):
        """Assert that the price in `result` is the one `expected`.

        `result` must be a PriceResult, whereas expected could a number.

        If `places` is not None, use
        `unittest.TestCase.assertAlmostEqual`:meth: instead of using
        `unittest.TestCase.assertEqual`:meth:.

        """
        if places is None:
            assertFn = self.assertEqual
        else:
            assertFn = partial(self.assertAlmostEqual, places=places)

        if isinstance(expected, PriceResult):
            assertFn(result.result, expected.result)
        else:
            assertFn(result.result, expected)


class DomainCaseMixin:
    "A mixin to to assert common domain tests"

    def assertEmpty(self, x, msg=None):
        "Assert that `x` is empty."
        if x:
            raise self.failureException(msg or f"{x} is not empty")

    def assertNonEmpty(self, x, msg=None):
        "Assert that `x` is not empty."
        if not x:
            raise self.failureException(msg or f"{x} is empty")

    def assertOverlap(self, a, b, msg=None):
        "Assert that `a` overlaps with `b`."
        r = a & b
        if not r:
            raise self.failureException(msg or f"{a} and {b} don't overlap")

    def assertDisjoint(self, a, b, msg=None):
        "Assert that `a` does not overlap with `b`."
        r = a & b
        if r:
            raise self.failureException(msg or f"{a} and {b} are not disjoint")


class PriceCase(unittest.TestCase, PriceCaseMixin):
    """A sub-class of `unittest.TestCase`:class: with `PriceCaseMixin`:class:"""

    pass


class KaboomProcedure:
    """A procedure that fails when called.

    This class doesn't implement the entire procotol of
    `~travertine.types.Procedure`:class: and cannot be translated to the Rust
    runtime.

    """

    def __call__(self, demand: Demand, env: Environment) -> PriceResultType:
        raise AssertionError("Should have been called")

    @property
    def avm(self):
        return {}


EMPTY_ENV: Environment = immutables.Map()
NULL_DEMAND = Demand(None, ())  # type: ignore
