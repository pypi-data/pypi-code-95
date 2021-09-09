#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotless.context import ReentrantContext


class MemoizedType(type):
    """Metaclass that automatically cache results.

    In the context of a single call-tree the same (equality, not identity)
    procedure will be called once for a given demand and environment.  Results
    will be shared forming a Directed Acyclic Graph (DAG) provided there are
    no cycles in the procedures themselves.

    """

    def __new__(cls, name, bases, attrs):
        call = attrs.get("__call__", None)
        if call is not None:
            attrs["__call__"] = cls._memoize_procedure(call)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def _memoize_procedure(cls, fn):
        from functools import wraps

        @wraps(fn)
        def result(self, demand, environment):
            from xotl.tools.symbols import Unset

            with cls._computation_context() as memory:
                key = (self, id(demand), id(environment))
                res = memory.get(key, Unset)
                if res is Unset:
                    memory[key] = res = fn(self, demand, environment)
                return res

        return result

    _computation_context = staticmethod(ReentrantContext(object()))
