#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Tools to test price tables"""
from types import GeneratorType
from typing import (
    AbstractSet,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from xotless.domains import EquivalenceSet as EqSet
from xotless.domains import IntervalSet
from xotless.ranges import Range

from .. import Program
from ..tables import NULL_FORMAT, ProcedureName, Table, TableFormat, generate_tables
from ..types import Procedure, TypedAttribute


def generate_full_tables(
    procedures: Sequence[Tuple[ProcedureName, Procedure]],
    table_format: TableFormat = NULL_FORMAT,
    now=None,
    chunk_size: int = 1000,
    _use_rust_runtime=False,
    rust_runtime: Optional[Mapping[Procedure, Program]] = None,
    lowerer=lambda x: x,
) -> Iterable[Table]:
    """Procedures the table prices but ensures to convert generators to list.

    All of the parameters except `lowerer` has the same meaning that in
    `travertine.tables.generate_tables`:func:.

    `lowerer` is callable to convert the cells of headers and rows to values
    which are nicer to test.  We provide the function `process_cell`:func:
    which convert common types found in price tables to strings.

    """
    for table in generate_tables(
        procedures,
        table_format,
        now=now,
        chunk_size=chunk_size,
        _use_rust_runtime=_use_rust_runtime,
        rust_runtime=rust_runtime,
    ):
        yield Table(
            table.name,
            (),  # we ignore this in tests
            tuple(lowerer(h) for h in table.columns_headers),
            read_table_rows(table, lowerer=lowerer),
        )


def read_table_rows(table: Table, lowerer=lambda x: x) -> List[Tuple[Any, ...]]:
    "Reads the rows of `table` and return the as list of tuples applying `lowerer`."
    rows: List[Tuple[Any, ...]] = []
    for original_row in table.rows:
        row: List[Any] = []
        for cell in original_row:
            if isinstance(cell, (GeneratorType, tuple)):
                for c in cell:
                    row.append(lowerer(c))
            else:
                row.append(lowerer(cell))
        rows.append(tuple(row))
    return rows


BASIC_VALUES = Union[str, float, int]

# PROCESS_CELL is actually a recursive type, which I don't want to express
# here; wherever Any appears, it should be actually PROCESSED_CELL
PROCESSED_CELL = Union[BASIC_VALUES, Sequence[Any], Dict[str, Any], AbstractSet[Any]]


def process_table_rows(rows: Iterable[Iterable[Any]]) -> List[Tuple[PROCESSED_CELL, ...]]:
    "Applies `process_row`:func: to all items in `rows`."
    return [process_row(row) for row in rows]


def process_row(row: Iterable[Any]) -> Tuple[PROCESSED_CELL, ...]:
    "Applies `process_cell`:func: to all items in `row`."
    return tuple(process_cell(c) for c in row)


def process_cell(v: Any) -> PROCESSED_CELL:
    """Convert the `v` to a basic types.

    Basic types are strings, float, int; and also sequences, sets and dicts of
    basic types.

    We convert common types to strings using a distinct format for each.  For
    instance, we convert `xotless.Range`:class: to `'{lower} - {upper}'` -- we
    don't distinguish between kinds of ranges.

    This function is useful as the argument to `lowerer` in
    `generate_full_tables`:func:.

    """
    if isinstance(v, TypedAttribute):
        return v.name
    elif isinstance(v, Range):
        lower, upper = v
        return f"{process_cell(lower)} - {process_cell(upper)}"
    elif isinstance(v, IntervalSet):
        return "{" + ",".join(str(process_cell(r)) for r in v.ranges) + "}"
    elif isinstance(v, EqSet):
        return f"{v.values}"
    elif isinstance(v, list):
        return [process_cell(x) for x in v]
    elif isinstance(v, (tuple, GeneratorType)):
        return tuple(process_cell(x) for x in v)
    elif isinstance(v, set):
        return {process_cell(x) for x in v}
    elif isinstance(v, dict):
        return {k: process_cell(x) for k, x in v.items()}
    elif isinstance(v, int):
        return v
    elif isinstance(v, float):
        # We may get minor differences like:
        #
        #  E   - [Table(attrs=(), columns_headers=('Price',), rows=[(690.93,)])]
        #  E   + [Table(attrs=(), columns_headers=('Price',), rows=[(690.9300000000001,)])]
        #
        # Rounding up to 8 digits should be enough for us.
        return round(v, 8)
    return str(v)
