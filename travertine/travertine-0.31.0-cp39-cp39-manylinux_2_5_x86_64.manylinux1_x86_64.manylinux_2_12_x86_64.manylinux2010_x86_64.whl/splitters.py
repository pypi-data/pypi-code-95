#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, TypeVar

from .types import Demand, Environment, Splitter


class BaseSplitter:  # pragma: no cover
    pass


T = TypeVar("T")


@dataclass(init=False, unsafe_hash=True)
class IdentitySplitter(BaseSplitter):
    "Don't split."

    def __call__(self, demand: T, env: Environment) -> Iterable[T]:
        return [demand]


@dataclass(init=False, unsafe_hash=True)
class RequestSplitter(BaseSplitter):
    "Split by each request."

    def __call__(self, demand: Demand, env: Environment) -> Iterable[Demand]:
        return [demand.replace(requests=(request,)) for request in demand.requests]


@dataclass(init=False, unsafe_hash=True)
class UnitSplitter(BaseSplitter):
    "Split by quantity (so that each item can be counted)."

    # Split the demand into a demand where each request is a unitary request
    # (quantity of 1) by repeating the same the request as many times as
    # needed.
    #
    # You might want to split first by request using `RequestSplitter`:class:.

    def __call__(self, demand: Demand, env: Environment) -> Iterable[Demand]:
        return [
            demand.replace(
                requests=tuple(
                    request.replace(quantity=1)
                    for request in demand.requests
                    for _ in range(math.ceil(request.quantity))
                )
            )
        ]


@dataclass(init=False, unsafe_hash=True)
class UnitRequestSplitter(BaseSplitter):
    "Split by request and units."

    # This combines both the splitter by requests and unit.  Each demand
    # contains as many requests as needed to make unitary requests of the
    # same commodity.

    def __call__(self, demand: Demand, env: Environment) -> Iterable[Demand]:
        return [
            demand.replace(
                requests=tuple(
                    request.replace(quantity=1)
                    for _ in range(math.ceil(request.quantity))
                )
            )
            for request in demand.requests
        ]


if TYPE_CHECKING:

    def check_splitter(splitter: Splitter) -> None:
        pass

    check_splitter(UnitSplitter())
    check_splitter(IdentitySplitter())
    check_splitter(RequestSplitter())
    check_splitter(UnitRequestSplitter())
