#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import contextlib

from xotl.tools.context import context


def ReentrantContext(context_identifier):
    """Return a reentrant context manager"""

    @contextlib.contextmanager
    def reentrant_context():
        ctx = context[context_identifier]
        if ctx:
            yield ctx["memory"]
        else:
            with context(context_identifier, memory={}) as ctx:
                yield ctx["memory"]

    return reentrant_context
