#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from ...formulae.ast import (
    AST,
    OPERATOR,
    BinaryOperation,
    LiteralNumber,
    Negation,
    Substep,
    Variable,
)

expressions: SearchStrategy[AST] = st.deferred(
    lambda: _expr_add_term | _expr_sub_term | _terms
)
formulae = expressions

_expr_add_term: SearchStrategy[BinaryOperation] = st.deferred(
    lambda: st.builds(BinaryOperation, st.just(OPERATOR.Add), expressions, _terms)
)
_expr_sub_term: SearchStrategy[BinaryOperation] = st.deferred(
    lambda: st.builds(BinaryOperation, st.just(OPERATOR.Sub), expressions, _terms)
)

_terms: SearchStrategy[AST] = st.deferred(
    lambda: _term_mul_factor | _term_floordiv_factor | _term_truediv_factor | _factors
)
_term_mul_factor: SearchStrategy[BinaryOperation] = st.deferred(
    lambda: st.builds(BinaryOperation, st.just(OPERATOR.Mult), _terms, _factors)
)
_term_floordiv_factor: SearchStrategy[BinaryOperation] = st.deferred(
    lambda: st.builds(BinaryOperation, st.just(OPERATOR.FloorDiv), _terms, _factors)
)
_term_truediv_factor: SearchStrategy[BinaryOperation] = st.deferred(
    lambda: st.builds(BinaryOperation, st.just(OPERATOR.Div), _terms, _factors)
)

_factors: SearchStrategy[AST] = st.deferred(
    lambda: variables | literal_numbers | substeps | _neg_exprs | expressions
)

# Since Negation can remove itself from tree in double-negation; the right
# result type is AST.
_neg_exprs: SearchStrategy[AST] = st.builds(Negation.of_expr, expressions)

variables: SearchStrategy[Variable] = st.builds(
    Variable, st.from_regex(r"""[^'"\r\n]+""", fullmatch=True)
)
substeps: SearchStrategy[Substep] = st.builds(
    Substep, st.integers(min_value=1, max_value=50)
)
literal_numbers: SearchStrategy[LiteralNumber] = st.builds(
    LiteralNumber, (st.integers() | st.floats(allow_infinity=False, allow_nan=False))
)
