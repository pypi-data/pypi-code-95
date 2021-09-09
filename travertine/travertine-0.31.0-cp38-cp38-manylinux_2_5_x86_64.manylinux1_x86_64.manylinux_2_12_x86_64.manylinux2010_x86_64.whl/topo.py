#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Topological sorting.

"""
from typing import Iterator, TypeVar

from xotless.walk import Node

T = TypeVar("T", bound=Node)


def topological_sort(node: T, key=id) -> Iterator[T]:
    """Return a topological sort of the graph reachable from Node.

    :param node: A node which complies with a Node interface.

    :param key: A function taking a node and producing a value to identify the
           node.  It defaults to `id`:func:.

    If a topological sort is not possible (i.e there are cycles ``a < b < ...
    a``), raise a RuntimeError.

    """
    done = set([])

    def walk(node):
        h = key(node)
        if h in done:
            return

        for child in node:
            yield from walk(child)
        done.add(h)
        yield node

    return walk(node)
