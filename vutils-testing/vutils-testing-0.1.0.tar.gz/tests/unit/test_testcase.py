#                                                         -*- coding: utf-8 -*-
# File:    ./tests/unit/test_testcase.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2021-09-11 08:30:17 +0200
# Project: vutils-testing: Auxiliary library for writing tests
#
# SPDX-License-Identifier: MIT
#
"""Test :mod:`vutils.testing.testcase` module."""

import unittest.mock

from vutils.testing.testcase import TestCase


class TestCaseTestCase(TestCase):
    """Test case for :class:`TestCase`."""

    def test_called_with(self):
        """Test :meth:`assert_called_with` method."""
        mock = unittest.mock.Mock()

        mock.foo()
        self.assert_called_with(mock.foo)

        mock.foo(1, 2)
        self.assert_called_with(mock.foo, 1, 2)

        mock.foo(bar=3, baz=4)
        self.assert_called_with(mock.foo, bar=3, baz=4)

        mock.foo(5, quux=6)
        self.assert_called_with(mock.foo, 5, quux=6)
