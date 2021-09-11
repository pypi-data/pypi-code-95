#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020, 2021 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Test print iteration
"""

from unittest import TestCase

from psprint import errors, print


class TestIter(TestCase):
    """
    These cases will always pass
    Tester should check the output if it is manually appealing
    by calling KeyboardInterrupt

    """
    def test_dict(self):
        obj = {'1': 1, '2': 2, '3': 3}
        print(obj, mark='bug', pref='dict', end='\n', iterate=True)
        print(obj, mark='info', iterate=False)
        # raise KeyboardInterrupt

    def test_list(self):
        obj = [1, 2, 3]
        print(obj, mark='bug', pref='list', iterate=True)
        print(obj, mark='info', iterate=False)
        # raise KeyboardInterrupt

    def test_generator(self):
        obj = (k for k in (1, 2, 3))
        print(obj, mark='bug', pref='gen', iterate=True)
        print(obj, mark='info', iterate=False)
        # raise KeyboardInterrupt

    def test_Tuple(self):
        obj = (1, 2, 3)
        print(obj, mark='bug', pref='tuple', iterate=True)
        print(obj, mark='info', iterate=False)
        # raise KeyboardInterrupt

    def test_nest(self):
        obj = (k for k in ([], {
            'a': 1,
            'b': [2, 'b'],
            3: {
                'int': 3,
                'bool': bin(3),
                'hex': hex(3)
            }
        }, {1, 2, 3, 4}, [['a', 'A'], ['b', 'B'], ['c', 'C']]))
        print(obj, mark='bug', pref='nest', iterate=True)
        print(obj, mark='info', iterate=False)
        # raise KeyboardInterrupt

    def test_deep_stack(self):
        obj = [[[[[[[[[[[[[[[[[], [], []]]]]]]]]]]]]]]]]
        self.assertWarns(errors.DeepIterWarning,
                         print,
                         obj,
                         mark='bug',
                         pref='deep',
                         iterate=True)
        print(obj, mark='info', iterate=False)

    def test_long_stack(self):
        obj = range(1000)
        self.assertWarns(errors.LongIterWarning,
                         print,
                         obj,
                         mark='bug',
                         pref='long',
                         iterate=True)
        print(obj, mark='info', iterate=False)
