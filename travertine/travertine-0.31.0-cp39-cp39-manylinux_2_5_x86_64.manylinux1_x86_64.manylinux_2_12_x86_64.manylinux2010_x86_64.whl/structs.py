#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Basic non-Odoo implementations of the types.

"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Iterable, Iterator, Optional, Sequence, Tuple, TypeVar, cast

import immutables
from xotl.tools.infinity import Infinity
from xotl.tools.symbols import Unset
from xotless.immutables import ImmutableWrapper

from . import ExternalObject, UnitaryDemand
from .i18n import _
from .types import Demand as TDemand
from .types import Environment, PriceResultType, Procedure, Result

try:
    from odoo.models import BaseModel
except ImportError:

    class BaseModel:  # type: ignore
        pass


S = TypeVar("S")


def _replace(self: S, **kwargs) -> S:
    from copy import copy

    # Ensure all values are hashable.  This will make the culprit more clear
    # in tracebacks.  We're getting some demands being passed a **list** of
    # requests.  But the error happens long after the demand was created.
    #
    # See #188: https://gitlab.merchise.org/mercurio-2018/xhg2/issues/188
    # See also MERCURIO-2019-BM: https://sentry.merchise.org/share/issue/47402a397b2b4e198a417102e818028a/
    for value in kwargs.values():
        hash(value)

    result = copy(self)
    result.__dict__.update(kwargs)
    return result


# NB: Don't put slots in Commodity, Request or Demand.  We use the __dict__ in
# the replace method.


@dataclass(unsafe_hash=True)
class Commodity:
    start_date: datetime
    duration: timedelta

    replace = _replace

    # FIXME: The __hash__ and __eq__ of Commodity don't take other injected
    # attributes into account

    @property
    def end_date(self):
        return self.start_date + self.duration


@dataclass(unsafe_hash=True)
class Request:
    commodity: Commodity
    quantity: int

    replace = _replace

    @classmethod
    def new(cls) -> "Request":
        """Return a new unitary request with a commodity starting now and during a
        day.

        """
        return cls(Commodity(datetime.utcnow(), timedelta(1)), 1)


@dataclass(unsafe_hash=True)
class Demand:
    date: datetime
    requests: Sequence[Request]

    replace = _replace

    def to_html(self):
        requests = " ".join(
            [
                f"<p>{getattr(r.commodity, 'name', str(r.commodity))}: {r.quantity}</p>"
                for r in self.requests
            ]
        )
        result = (
            f"<p><strong>Demand date:&nbsp;</strong>{self.date.strftime('%F %H:%m')}</p>"
        )
        if requests:
            result += f"<strong>Demand requests:</strong>{requests}"
        return result

    def get_commodities(self) -> Iterable[Commodity]:
        return tuple(r.commodity for r in self.requests)

    @classmethod
    def from_commodities(cls, commodites: Sequence[Commodity], date=None) -> "Demand":
        return cls.from_requests((Request(c, 1) for c in commodites), date=date)

    @classmethod
    def from_requests(cls, requests: Iterable[Request], date=None) -> "Demand":
        return cls(date=date or datetime.utcnow(), requests=tuple(requests))

    def to_unitary_demand(self) -> UnitaryDemand:
        """Return a unitary demand from this one if possible.

        If this is not an unitary demand (one with a single request)
        raise a ValueError.

        """
        if len(self.requests) == 1:
            request = self.requests[0]
            commodity = request.commodity
            attrs = {
                key: _convert_to_runtime_value(value)
                for key, value in commodity.__dict__.items()
                if not key.startswith("_") and _allowable_runtime_value(value)
            }
            if commodity.duration is not None:
                attrs["duration"] = commodity.duration
            return UnitaryDemand(
                self.date,
                request.quantity,
                # UnitaryDemand will TypeError if start_date or duration
                # are None, and we create all commodities of price tables
                # with those values set to None.  If we're still getting
                # those values here is because the price program doesn't
                # use them, so let's put any value.
                commodity.start_date or self.date,
                attrs,
            )
        else:
            raise ValueError(f"Expected a unitary demand and got {self}")


@dataclass(init=False, unsafe_hash=True)
class PriceResult:
    """The result of price computation.

    The procedure can provide a `title` for the `result`, and also
    sub-results to provide insight about how the price was computed.

    """

    title: str
    procedure: Optional[Procedure]
    result: Result
    # A price result has several 'children' result which contain information
    # about the method used to compute `result` and `title`.
    #
    # There's no a pre-established requirement between the `result` of the
    # children and the parent's result.
    #
    # It's up to the program to create the information.
    subresults: Tuple[PriceResultType[Commodity], ...] = field(compare=False)

    # The same procedure can be used iteratively to compute sub-demands.  Also
    # the environment can change from one call to the other.  The only way to
    # distinguish price results resulting from the same procedure is to know
    # both the demand priced and the environment.
    demand: TDemand
    env: Environment

    def __init__(
        self,
        title: str,
        procedure: Optional["Procedure"],
        result: Result,
        demand: TDemand,
        env: Environment,
        *subresults: PriceResultType[Commodity],
    ) -> None:
        self.title = title
        self.procedure = procedure
        self.result = result
        self.demand = demand
        self.env = env
        self.subresults = tuple(subresults)

    replace = _replace

    def __str__(self):
        import textwrap

        subresults = [textwrap.indent(str(r), " - ") for r in self.subresults]
        if isinstance(self.result, (int, float)):
            result = f"{self.title!s} = {self.result:.2f}"
        else:
            result = f"{self.title!s} = {self.result!s}"
        if not subresults:
            return f"{result}."
        else:
            return "\n".join([f"{result}:"] + subresults)

    def to_html(self):
        subresults = [r.to_html() for r in self.subresults]
        if isinstance(self.result, (int, float)):
            result = f"{self.title!s} = {self.result:.2f}"
        else:
            result = f"{self.title!s} = {self.result!s}"
        if not subresults:
            return f"<p>{result}</p>"
        else:
            return "\n".join(
                [f"<details><summary>{result}:</summary>"] + subresults + ["</details>"]
            )


@dataclass
class LazyCall:
    """A lazy call to a procedure."""

    proc: Procedure
    demand: TDemand
    env: Environment

    def __call__(self) -> PriceResultType:
        return self.proc(self.demand, self.env)


@dataclass(init=False)
class LazyResults(Sequence[PriceResultType]):
    """Represents many results which are computed on demand.

    I assume that `partials` are memoized so that calling twice only performs
    the first computation.

    """

    partials: Sequence[LazyCall]

    def __init__(self, partials: Iterable[LazyCall]) -> None:
        self.partials = partials = tuple(partials)
        self.results = [cast(PriceResultType, Unset)] * len(partials)

    @property
    def _pairs(self) -> Iterable[Tuple[PriceResultType, LazyCall]]:
        return zip(self.results, self.partials)

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        result = self.results[index]
        if result is Unset:
            partial = self.partials[index]
            self.results[index] = result = partial()
        return result

    def __iter__(self) -> Iterator[PriceResultType]:
        for index, (result, partial) in enumerate(zip(self.results, self.partials)):
            if result is Unset:
                self.results[index] = result = partial()
            yield result


class LazyPriceResult(PriceResult):
    def __init__(
        self,
        title: str,
        procedure: Optional[Procedure],
        result: Result,
        demand: TDemand,
        env: Environment,
        subresults: Sequence[PriceResultType],
    ) -> None:
        super().__init__(title, procedure, result, demand, env)
        self.subresults = subresults  # type: ignore

    def __str__(self):
        import textwrap

        def _str(r, partial):
            if r is Unset:
                name = str(partial.proc)
                title = getattr(
                    partial.proc, "title", _("Procedure {name}").format(name=name)
                )
                return _("{title} was optimized away").format(title=title)
            else:
                return str(r)

        subresults = [
            textwrap.indent(_str(r, partial), " - ")
            for r, partial in self.subresults._pairs
        ]
        result = f"{self.title} = {self.result}"
        if not subresults:
            return f"{result}."
        else:
            return "\n".join([f"{result}:"] + subresults)

    def to_html(self):
        def _to_html(r, partial):
            if r is Unset:
                name = str(partial.proc)
                title = getattr(
                    partial.proc, "title", _("Procedure {name}").format(name=name)
                )
                return _("<p>{title} was optimized away<p>").format(title=title)
            else:
                return r.to_html()

        subresults = [_to_html(r, partial) for r, partial in self.subresults._pairs]
        result = f"{self.title} = {self.result}"
        if not subresults:
            return f"<p>{result}</p>"
        else:
            return "\n".join(
                [f"<details><summary>{result}:</summary>"] + subresults + ["</details>"]
            )


def _convert_to_runtime_value(v: Any) -> Any:
    if isinstance(v, type(Infinity)):
        return None
    if isinstance(v, ImmutableWrapper):
        v = v._ImmutableWrapper__target
    to_external_object = getattr(type(v), "_to_travertine_external_object_", None)
    if to_external_object:
        res = to_external_object(v)
        if not isinstance(res, ExternalObject):
            raise TypeError(
                "_to_travertine_external_object must return ExternalObject.  "
                f"Class '{v.__class__}' returned '{res.__class__}'"
            )
        v = res
    if isinstance(v, BaseModel):
        return ExternalObject(v._name, v.id)
    return v


def _allowable_runtime_value(v: Any) -> bool:
    res = _convert_to_runtime_value(v)
    return isinstance(res, (float, int, str, datetime, timedelta, ExternalObject))


del _replace


NULL_DEMAND: Demand = Demand.from_requests(())
EMPTY_ENV: Environment = immutables.Map()
