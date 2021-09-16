# Copyright 2017 Okera Inc.
#

from __future__ import absolute_import

import builtins
import warnings
import logging
from logging import NullHandler
import string
import random

import six

from okera._thrift_api import (
    TExprType,
)

def get_logger_and_init_null(logger_name):
    logger = logging.getLogger(logger_name)
    logger.addHandler(NullHandler())
    return logger

log = get_logger_and_init_null(__name__)

def _random_id(prefix='', length=8):
    return prefix + ''.join(random.sample(string.ascii_uppercase, length))

def to_bytes(text):
    if isinstance(text, builtins.bytes):
        # We already have bytes, so do nothing
        return text
    if isinstance(text, list):
        # Convert a list of integers to bytes
        return builtins.bytes(text)
    # Convert UTF-8 text to bytes
    return builtins.bytes(str(text), encoding='utf-8')

def _escape(s):
    e = s
    e = e.replace('\\', '\\\\')
    e = e.replace('\n', '\\n')
    e = e.replace('\r', '\\r')
    e = e.replace("'", "\\'")
    e = e.replace('"', '\\"')
    log.debug('%s => %s', s, e)
    return e


def _py_to_sql_string(value):
    if value is None:
        return 'NULL'
    elif isinstance(value, six.string_types):
        return "'" + _escape(value) + "'"
    return str(value)

# Logging-related utils

def warn_deprecate(functionality='This', alternative=None):
    msg = ("{0} functionality in pyokera is now deprecated and will be removed "
           "in a future release".format(functionality))
    if alternative:
        msg += "; Please use {0} instead.".format(alternative)
    warnings.warn(msg, Warning)

class ExprUtils():
    """
    Utility class for handling expression ASTs
    """
    @staticmethod
    def convert_expr_ast_to_json(expr):
        """ Converts an expression AST to a python representation. This
            returns a dictionary that represents the AST. """
        root = None
        idx = 0
        while idx < len(expr.nodes):
            node, idx = ExprUtils.__convert_expr_ast_to_json_helper(expr.nodes, idx)
            if root is None:
                root = node
        return root

    @staticmethod
    def __convert_expr_ast_to_json_helper(nodes, idx):
        """ Utility for AST conversion. Thrift requires trees be serialized as
            lists, so this does the conversion."""
        node = nodes[idx]
        idx = idx + 1

        converted = {}
        converted['sql'] = node.sql
        if node.type == TExprType.LITERAL:
            converted['type'] = 'LITERAL'
        elif node.type == TExprType.OPERATOR:
            converted['type'] = 'OPERATOR'
        elif node.type == TExprType.FUNCTION:
            converted['type'] = 'FUNCTION'
        elif node.type == TExprType.ATTRIBUTE:
            converted['type'] = 'ATTRIBUTE'
        elif node.type == TExprType.COLUMN:
            converted['type'] = 'COLUMN'

        if node.num_children > 0:
            children = []
            for i in range(0, node.num_children):
                c, idx = ExprUtils.__convert_expr_ast_to_json_helper(nodes, idx)
                children.append(c)
            converted['children'] = children
        return converted, idx
