#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import ast
import enum
from dataclasses import dataclass
from typing import Optional, Union


class AST:
    # Marker class for the formula AST

    @property
    def ql(self):
        raise NotImplementedError

    @property
    def evm(self):
        return {}

    @property
    def max_substep_index(self):
        "The max substep index used in the AST.  Zero means no-substep used."
        return 0

    def walk(self):
        raise NotImplementedError


@dataclass
class Variable(AST):
    varname: str

    def __str__(self):
        return f"'{self.varname}'"

    @property
    def ql(self):
        return ast.Call(
            make_attr(ast.Name("env", ast.Load()), "get"),
            [ast.Str(self.varname), ast.Name("Undefined", ast.Load())],
            [],
        )

    @property
    def evm(self):
        return {self.varname: 0}

    def walk(self):
        yield self


@dataclass
class Substep(AST):
    index: int

    def __str__(self):
        return f"#{self.index}"

    @property
    def ql(self):
        return make_attr(
            ast.Call(
                ast.Subscript(
                    ast.Name("procedures", ast.Load()),
                    # Python is 0-based indexes, but our little language is
                    # 1-based.
                    ast.Index(ast.Num(self.index - 1)),
                    ast.Load(),
                ),
                [ast.Name("demand", ast.Load()), ast.Name("env", ast.Load())],
                [],
            ),
            "result",
        )

    @classmethod
    def from_literal(cls, literal):
        value = int(literal, 10)
        if value <= 0:
            raise ValueError(f"Invalid index for a substep: #{value}")
        return cls(int(literal, 10))

    @property
    def max_substep_index(self):
        return self.index

    def walk(self):
        yield self


@dataclass
class LiteralNumber(AST):
    number: Union[float, int]

    def __str__(self):
        return repr(self.number)

    @property
    def ql(self):
        return ast.Num(self.number)

    @classmethod
    def from_literal(cls, source):
        if "." in source or "e" in source or "E" in source:
            return cls(float(source))
        else:
            return cls(int(source))

    def walk(self):
        yield self


class OPERATOR(enum.Enum):
    # NOTICE: The choice of the names is given by the names of the operators
    # in the ast

    Add = "+"
    Sub = "-"
    FloorDiv = "//"
    Div = "/"
    Mult = "*"

    def __str__(self):
        return f"OPERATOR.{self.name}"

    __repr__ = __str__

    @property
    def ql(self):
        return getattr(ast, self.name)()


@dataclass
class BinaryOperation(AST):
    operator: OPERATOR
    left: Optional[AST] = None
    right: Optional[AST] = None

    def __str__(self):
        return f"({self.left}) {self.operator.value} ({self.right})"

    @property
    def ql(self):
        return ast.BinOp(self.left.ql, self.operator.ql, self.right.ql)

    @property
    def evm(self):
        result = self.left.evm
        result.update(self.right.evm)
        return result

    @property
    def max_substep_index(self):
        return max(self.left.max_substep_index, self.right.max_substep_index)

    def walk(self):
        """Generate a post-fix walk of the AST node."""
        yield from self.left.walk()
        yield from self.right.walk()
        yield self


@dataclass
class Negation(AST):
    expr: AST

    @classmethod
    def of_expr(cls, expr: AST) -> AST:
        if isinstance(expr, Negation):
            return expr.expr
        elif isinstance(expr, LiteralNumber):
            return LiteralNumber(-expr.number)
        else:
            return cls(expr)

    def __str__(self):
        return f"-({self.expr})"

    @property
    def ql(self):
        return ast.UnaryOp(ast.USub(), self.expr.ql)

    @property
    def evm(self):
        return self.expr.evm

    @property
    def max_substep_index(self):
        return self.expr.max_substep_index

    def walk(self):
        """Generate a post-fix walk of the AST node."""
        yield from self.expr.walk()
        yield self


def make_attr(node, attr):
    return ast.Attribute(node, attr, ast.Load())  # noqa
