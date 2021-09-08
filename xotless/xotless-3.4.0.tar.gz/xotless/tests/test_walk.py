#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import doctest

import xotless.walk

from .support import captured_stderr, captured_stdout


def test_doctests():
    with captured_stdout() as stdout, captured_stderr() as stderr:
        failure_count, test_count = doctest.testmod(
            xotless.walk,
            verbose=True,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            raise_on_error=False,
        )
    if test_count and failure_count:  # pragma: no cover
        print(stdout.getvalue())
        print(stderr.getvalue())
        raise AssertionError("pruned_prefix_walk doctest failed")
