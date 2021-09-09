#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from ply import lex, yacc

from .ast import OPERATOR, BinaryOperation, LiteralNumber, Negation, Substep, Variable

tokens = [
    "VARIABLE",
    "SUBSTEP",
    "LITERAL_NUMBER",
    "ADD",
    "SUB",
    "TRUEDIV",
    "FLOORDIV",
    "MUL",
    "LPAREN",
    "RPAREN",
]


def t_VARIABLE(t):
    r"""('[^']+'|"[^"]+")"""
    t.value = t.value[1:-1]
    return t


def t_SUBSTEP(t):
    r"(\#|\$)[1-9]\d*"  # avoid bogus #0, or #01
    t.value = t.value[1:]
    return t


def t_LITERAL_NUMBER(t):
    r"\d+(\.\d+)?([eE][\-\+]?\d+)?"
    t.type = "LITERAL_NUMBER"
    return t


def t_LITERAL_NUMBER_float_repr_starting_with_dot(t):
    r"\.\d+([eE][\-\+]?\d+)?"
    t.type = "LITERAL_NUMBER"
    return t


def t_LPAREN(t):
    r"\("
    return t


def t_RPAREN(t):
    r"\)"
    return t


def t_ADD(t):
    r"\+"
    return t


def t_SUB(t):
    r"\-"
    return t


def t_FLOORDIV(t):
    r"//"
    return t


def t_TRUEDIV(t):
    r"/"
    return t


def t_MUL(t):
    r"\*"
    return t


t_ignore = " \t\n\r"


lexer = lex.lex(debug=False)


def p_add_expression(prod):
    "expr : expr ADD term"
    left, right = prod[1], prod[3]
    prod[0] = BinaryOperation(OPERATOR.Add, left, right)


def p_sub_expression(prod):
    "expr : expr SUB term"
    left, right = prod[1], prod[3]
    prod[0] = BinaryOperation(OPERATOR.Sub, left, right)


def p_term_expression(prod):
    "expr : term"
    prod[0] = prod[1]


def p_mul_term(prod):
    "term : term MUL factor"
    left, right = prod[1], prod[3]
    prod[0] = BinaryOperation(OPERATOR.Mult, left, right)


def p_floordiv_term(prod):
    "term : term FLOORDIV factor"
    left, right = prod[1], prod[3]
    prod[0] = BinaryOperation(OPERATOR.FloorDiv, left, right)


def p_truediv_term(prod):
    "term : term TRUEDIV factor"
    left, right = prod[1], prod[3]
    prod[0] = BinaryOperation(OPERATOR.Div, left, right)


def p_factor_term(prod):
    "term : factor"
    prod[0] = prod[1]


def p_factor_variable(prod):
    "factor : VARIABLE"
    prod[0] = Variable(prod[1])


def p_factor_literal_number(prod):
    "factor : LITERAL_NUMBER"
    prod[0] = LiteralNumber.from_literal(prod[1])


def p_factor_negative_expr(prod):
    "factor : SUB expr"
    prod[0] = Negation.of_expr(prod[2])


def p_factor_substep(prod):
    "factor : SUBSTEP"
    prod[0] = Substep.from_literal(prod[1])


def p_factor_expr(prod):
    "factor : LPAREN expr RPAREN"
    prod[0] = prod[2]


def p_error(prod):
    raise ValueError(f"SyntaxError at {prod}")


expr_parser = yacc.yacc(debug=False, start="expr", tabmodule="expr_parsertab")
