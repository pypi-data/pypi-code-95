#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from datetime import datetime, timedelta, timezone

from hypothesis import strategies

from ...structs import Commodity as BaseCommodity
from ...structs import Demand, Request

# Generate start dates at 16hrs and end dates at noon.
MIN_DATETIME = datetime(2000, 1, 1)
MAX_DATETIME = datetime(3000, 12, 31)
_sharp = dict(hour=16, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)

sensible_durations = strategies.integers(min_value=1, max_value=10).map(
    lambda days: timedelta(hours=days * 24 - 4)
)
sensible_start_dates = strategies.datetimes(
    min_value=MIN_DATETIME,
    max_value=MAX_DATETIME,
    allow_imaginary=False,
    timezones=strategies.just(timezone.utc),
).map(
    lambda d: d.replace(**_sharp)  # type: ignore
)

prices = strategies.integers(min_value=1, max_value=10 ** 12)
sensible_pax_counts = strategies.integers(min_value=1, max_value=100)


class Commodity(BaseCommodity):
    @property
    def duration_in_days(self):
        # This is the 20/24 hours a night; ie. the last night is 20 hours, but
        # all others are 24 hours.
        #
        # It will be off with duration.days by at most 1 day.
        hours = self.duration.total_seconds() // 3600
        return (hours + 4) // 24


@strategies.composite
def commodities(draw):
    """Generate objects of type Commodity.

    To make some tests easier, every commodity will have an additional
    attribute 'standard_price' (with values drawn from `prices`:any:).

    """
    start_date = draw(sensible_start_dates)
    duration = draw(sensible_durations)
    standard_price = draw(prices)
    pax = draw(sensible_pax_counts)
    result = Commodity(start_date=start_date, duration=duration)
    result.standard_price = standard_price
    result.pax_count = pax
    assert (
        abs(result.duration_in_days - duration.days) <= 1
    ), f"{result.duration_in_days} != {duration.days} [+- 1]; duration is {duration} {type(duration)}"
    return result


@strategies.composite
def demands(draw, items=None, max_size=20, min_size=1):
    """A Hypothesis strategies that generates demands."""
    if items is None:
        items = requests()
    date = draw(sensible_start_dates).replace(hour=8)
    ls = strategies.lists(items, min_size=min_size, max_size=max_size)
    rqs = draw(ls)
    return Demand.from_requests(date=date, requests=rqs)


def requests(items=None, quantities=None):
    if quantities is None:
        quantities = strategies.integers(min_value=1, max_value=10)
    return strategies.tuples(commodities() if items is None else items, quantities).map(
        lambda data: Request(commodity=data[0], quantity=data[1])
    )
