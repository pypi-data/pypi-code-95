#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from collections import deque
from dataclasses import dataclass
from typing import Iterator

from typing_extensions import Protocol
from xotl.tools.string import cut_prefix, cut_suffix


# fmt: off
class Node(Protocol):
    def __hash__(self): ...
    def __iter__(self) -> Iterator["Node"]: ...
# fmt: on


@dataclass(unsafe_hash=True)
class NodeRef:
    "A wrapper around a node in walks."
    node: Node

    def __repr__(self):
        node = cut_suffix(cut_prefix(repr(self.node), "<"), ">")
        return f"<&{node}>"


def pruned_prefix_walk(
    node: Node, prune_entirely: bool = False
) -> Iterator[NodeRef]:
    r"""Produced a pruned prefix walk of a Directed Acyclic Graph.

    By default, pruned means that the same subgraph is never yielded more than
    once.  However to provide the full information for every node in the graph
    we yield references to nodes.  This allows to *repeat* nodes without yield
    the whole subgraph. If `pruned_entirely` is True, never yield the same
    node more than once.

    Example:

    Let's make a graph like this::

        a ------> c -----------------.
        |        / \                 |
        | .-----'   '----\           v
        | |               '-> f <--- e
        v v                   |
         b  -----> d <--------'

    First, just boilerplate to have a Item which has the Node interface:

        >>> from dataclasses import dataclass
        >>> from typing import Tuple

        >>> @dataclass(unsafe_hash=True)
        ... class Item:
        ...     name: str
        ...     children: Tuple["Item", ...]
        ...     def __iter__(self):
        ...         return iter(self.children)
        ...     def __repr__(self):
        ...         return f"<{self.name}>"

    Now, let's build the graph:

        >>> d = Item("d", ())
        >>> f = Item("f", (d, ))
        >>> e = Item("e", (f, ))
        >>> b = Item("b", (d, ))
        >>> c = Item("c", (b, f, e))
        >>> a = Item("a", (b, c))

    And finally, let's walk the graph:

        >>> from xotless.walk import pruned_prefix_walk
        >>> list(pruned_prefix_walk(a))
        [<&a>, <&b>, <&d>, <&c>, <&b>, <&f>, <&d>, <&e>, <&f>]

    Notice that we reach node 'b' a second time when coming from node 'c', yet
    this time we don't follow 'b' and that's why we don't yield 'd'
    immediately after the second yield of 'b'.  Nevertheless, node 'd' does
    appear a second time, but because reach it from node 'f'.

    If `prune_entirely` is set to True we don't get any duplicate:

        >>> list(pruned_prefix_walk(a, prune_entirely=True))
        [<&a>, <&b>, <&d>, <&c>, <&f>, <&e>]


    """
    memory = set([])
    nodes = deque([node])
    while nodes:
        current = nodes.popleft()
        yield NodeRef(current)
        if current not in memory:
            memory.add(current)
            children = [
                n
                for n in iter(current)
                if not prune_entirely or n not in memory
            ]
            children.reverse()
            nodes.extendleft(children)
