#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""The parser for the Very Simple Expression Formulae.

The grammar is that of is a very simple arithmetical expression (with just
'+', '-', '*', '//', and '/'), variables names enclosed in single quotes and
substeps indexes with start with '$'.

Example::

    'variable 1' + $1 * ($2 + 10 - "variable 2")

Notes:

- Substep indexes start at 1: $1, $2, ...  The order is given by the orden in
  the list of substeps.

- Variables are ALWAYS enclosed in single or double quotes; even if they have
  no spaces and such.

"""
from __future__ import absolute_import

import ast as pyast
import sys
from typing import Callable, Tuple

from ply.lex import LexError
from ply.yacc import YaccError

from ..types import Demand, Environment, Procedure, Result, Undefined
from .ast import AST
from .parser import expr_parser, lexer

FormulaProcedureType = Callable[[Demand, Environment, Tuple[Procedure, ...]], Result]


def parse(code: str, *, debug=False, tracking=False) -> AST:
    """Parse the `code` and return an AST."""
    try:
        return expr_parser.parse(code, lexer=lexer, debug=debug, tracking=tracking)
    except (LexError, YaccError, ValueError):
        raise ValueError("Invalid code: '{code}'".format(code=code))


def transpile(parsed: AST, *, name="<transpiled>") -> FormulaProcedureType:
    """Transpile the parsed AST to Python-executable callable."""
    return eval(
        compile(
            ensure_compilable(
                pyast.Expression(
                    pyast.Lambda(make_arguments("demand", "env", "procedures"), parsed.ql)
                )
            ),
            name,
            "eval",
        ),
        {"Undefined": Undefined},
    )


def make_arguments(*names):
    if (3, 4) <= _py_version < (3, 8):
        return pyast.arguments(  # noqa
            args=[pyast.arg(name, None) for name in names],  # noqa
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )
    if (3, 8) <= _py_version:
        return pyast.arguments(  # noqa
            posonlyargs=[],
            args=[pyast.arg(name, None) for name in names],  # noqa
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )
    else:
        assert False  # pragma: no cover


def ensure_compilable(st):
    visitor = SetAttributesVisitor(lineno=1, col_offset=0)
    visitor.visit(st)
    return st


class SetAttributesVisitor(pyast.NodeVisitor):
    def __init__(self, **attrs):
        self.attrs = attrs

    def generic_visit(self, node):
        from xotl.tools.symbols import Unset

        get = lambda a: getattr(node, a, Unset)  # noqa
        for attr, val in self.attrs.items():
            if get(attr) is Unset:
                setattr(node, attr, val)
        return super(SetAttributesVisitor, self).generic_visit(node)


_py_version = sys.version_info
_py3 = _py_version >= (3, 0)
del sys
