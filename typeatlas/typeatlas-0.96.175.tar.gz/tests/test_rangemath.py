# -*- coding: utf-8 -*-
#
#    TypeAtlas Unit Tests for Range Math
#    Copyright (C) 2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

import os
import nose
from nose.tools import assert_equal, assert_not_equal, assert_raises
from nose.tools import assert_sequence_equal, assert_set_equal
from nose.tools import assert_less_equal, assert_greater_equal
from nose.tools import assert_set_equal, assert_in, assert_not_in
from itertools import chain, product

if os.environ.get('TYPEATLAS_DEBUG_TYPECHECK'):
    from typeguard.importhook import install_import_hook
    install_import_hook('typeatlas')

from typeatlas.rangemath import OrdinalRange, CharacterRange, MultiRange
from typeatlas.rangemath import RangeBase, EMPTY_RANGE
from typeatlas.blockmath import intersection, have_intersection, iterblocks
from typeatlas.blockmath import intersect_many, blockslen
from typeatlas.util import OrderedSet

int_members = {-2000, -1000, 1,2,3,4,202,1001, 1662, 100248, 1000000000000000}

sets = [
    set(),
    {1,2,3,5,6,7,10,12,13},
    {2,3,7,10},
    {8},
    {2,3,7,8,10},
    {2,3,7,8,9},
    OrderedSet([100,14,3,13]),
    {101, 100, 14,12},
    {102, 101, 100, 14,13,12},
]

ordinal_range_pairs = [
    (OrdinalRange(1,5), OrdinalRange(-1,7)),
    (OrdinalRange(1,5), OrdinalRange(0,6)),
    (OrdinalRange(1,5), OrdinalRange(1,7)),
    (OrdinalRange(1,5), OrdinalRange(0,5)),
    (OrdinalRange(1,5), OrdinalRange(0,3)),
    (OrdinalRange(1,5), OrdinalRange(3,7)),
    (OrdinalRange(1,5), OrdinalRange(5,7)),
    (OrdinalRange(1,5), OrdinalRange(6,8)),
    (OrdinalRange(1,5), OrdinalRange(5,6)),
    (OrdinalRange(1,5), OrdinalRange(2,3)),
    (OrdinalRange(1,5), OrdinalRange(2,4)),
    (OrdinalRange(1,5), EMPTY_RANGE),
    (MultiRange([OrdinalRange(1,5), OrdinalRange(7,12)]),
     MultiRange([OrdinalRange(-1,3), OrdinalRange(8,15)])),
    (MultiRange([OrdinalRange(1,5), OrdinalRange(7,12)]),
     MultiRange([OrdinalRange(8,15), OrdinalRange(-1,3)])),
    (MultiRange([OrdinalRange(1,5), OrdinalRange(7,12)]),
     MultiRange([OrdinalRange(3,6), OrdinalRange(8,15)])),
    (MultiRange([OrdinalRange(1,5), OrdinalRange(7,12)]),
     MultiRange([OrdinalRange(-1,3), OrdinalRange(6,11)])),
    (MultiRange([OrdinalRange(1,5), OrdinalRange(7,12)]),
     OrdinalRange(3, 11)),
    (MultiRange([OrdinalRange(1,5), OrdinalRange(7,12)]),
     MultiRange([OrdinalRange(-1,3), OrdinalRange(8,15)])),
    (OrdinalRange.fromstring('5-100 303-581 2547-15824 16821-154775'),
     OrdinalRange.fromstring('80-1555 5666-1577922')),

]

char_members = CharacterRange.fromstring('a-z A-Z 0-9')

character_range_pairs = [
    (CharacterRange('a','z'), CharacterRange('A','Z')),
    (CharacterRange('a','z'), CharacterRange('A','c')),
    (CharacterRange('G','z'), CharacterRange('A','Z')),
    (CharacterRange.fromstring('a-c d-f w-z'),
     CharacterRange.fromstring('b-p q-x')),
]


def all_sets():
    yield from sets

def all_ranges():
    yield from chain.from_iterable(ordinal_range_pairs)
    yield from chain.from_iterable(character_range_pairs)

def all_setlike():
    yield from all_sets()
    yield from all_ranges()

def all_pairs():
    yield from ordinal_range_pairs
    yield from character_range_pairs
    yield from product(map(OrdinalRange.from_iterable, sets),
                       map(OrdinalRange.from_iterable, sets))


class TestRange:

    def test_contains(self):
        int_vals = set(int_members)
        for rg in chain.from_iterable(ordinal_range_pairs):
            if len(rg) < 1000:
                int_vals.update(rg)

        for s in chain(all_sets(),
                       chain.from_iterable(ordinal_range_pairs)):
            if isinstance(s, RangeBase):
                rg = s
                s = set(rg)
            else:
                rg = OrdinalRange.from_iterable(s)

            for val in s:
                assert_in(val, rg)
            for val in int_vals:
                if val in s:
                    continue
                assert_not_in(val, rg)

            if rg:
                assert_in(rg.ranges[0].start, rg)
                assert_in(rg.ranges[-1].end, rg)
                assert_in(rg.ranges[0].start, s)
                assert_in(rg.ranges[-1].end, s)

                assert_not_in(rg.ranges[0].start - 1, rg)
                assert_not_in(rg.ranges[-1].end + 1, rg)
                assert_not_in(rg.ranges[0].start - 1, s)
                assert_not_in(rg.ranges[-1].end + 1, s)

        char_vals = set(char_members)
        for rg in chain.from_iterable(character_range_pairs):
            s = set(rg)

            for val in s:
                assert_in(val, rg)
            for val in char_vals:
                if val in s:
                    continue
                assert_not_in(val, rg)

    def test_successor(self):
        int_vals = set(int_members)

        for s in chain(all_sets(),
                       chain.from_iterable(ordinal_range_pairs)):
            if isinstance(s, RangeBase):
                rg = s
                s = set(rg)
            else:
                rg = OrdinalRange.from_iterable(s)

            if not rg:
                continue

            for val in chain(int_vals, s,
                             [rg.ranges[0].start, rg.ranges[0].end]):
                assert_equal(val + 1, rg.successor(val))
                assert_equal(val - 1, rg.predecessor(val))

        char_vals = set(char_members)
        for rg in chain.from_iterable(character_range_pairs):
            s = set(rg)
            for val in chain(char_vals, s,
                             [rg.ranges[0].start, rg.ranges[0].end]):

                assert_equal(chr(ord(val) + 1), rg.successor(val))
                assert_equal(chr(ord(val) - 1), rg.predecessor(val))

    def test_bool(self):
        for s in chain(all_sets(),
                       chain.from_iterable(ordinal_range_pairs),
                       chain.from_iterable(character_range_pairs)):
            if isinstance(s, RangeBase):
                rg = s
                s = set(rg)
            else:
                rg = OrdinalRange.from_iterable(s)

            assert_equal(bool(s), bool(rg))

    def test_round_trip_sets(self):
        for s in all_sets():
            rg = OrdinalRange.from_iterable(s)
            rebuilt = set(rg)
            assert_equal(set(s), set(rg), [s, rg])
            assert_equal(s, rg, [s, rg])
            assert_equal(s, rebuilt, [s, rg, rebuilt])

    def test_round_trip_ranges(self):
        for rg in all_ranges():
            s = set(rg)

            if not s:
                rebuilt = OrdinalRange.from_iterable(s)
            else:
                rebuilt = rg.range_type.from_iterable(s)
            assert_equal(set(s), set(rg), [s, rg])
            assert_equal(s, rg, [s, rg])
            assert_equal(s, rebuilt, [s, rg])

    def test_round_trip_string(self):
        for rg in all_ranges():
            s = rg.tostring()
            if not rg:
                rebuilt = OrdinalRange.fromstring(s)
            else:
                rebuilt = rg.range_type.fromstring(s)
            assert_equal(rebuilt, rg, [rg, rg.tostring()])

    def test_round_trip_fontconfig(self):
        for rg in all_ranges():
            if rg and (rg.value_type is str or rg.ranges[0].start < 0):
                continue
            s = rg.to_fontconfig()
            if not rg:
                rebuilt = OrdinalRange.from_fontconfig(s)
            else:
                rebuilt = rg.range_type.from_fontconfig(s)
            assert_equal(rebuilt, rg, [rg, s, rg.tostring()])

    def test_round_trip_blocks(self):
        for rg in all_ranges():
            if rg and rg.value_type is str:
                continue

            s = rg.to_blocks()
            if not rg:
                rebuilt = OrdinalRange.from_blocks(s)
            else:
                rebuilt = rg.range_type.from_blocks(s)
            assert_equal(rebuilt, rg, [rg, rg.tostring()])

    def test_round_trip_plain_blocks(self):
        for rg in all_ranges():
            if rg and rg.value_type is str:
                continue

            s = rg.to_plain_blocks()
            if not rg:
                rebuilt = OrdinalRange.from_blocks(s)
            else:
                rebuilt = rg.range_type.from_blocks(s)
            assert_equal(rebuilt, rg, [rg, rg.tostring()])

    def test_eq_true(self):
        for rg in all_ranges():
            assert_equal(set(rg), set(rg), rg)
            assert_equal(rg, rg, rg)

    def test_eq_others(self):
        for left, right in all_pairs():
            if set(left) == set(right):
                assert_equal(left, right, [left, right])
                assert_equal(right, left, [left, right])
            else:
                assert_not_equal(left, right, [left, right])
                assert_not_equal(right, left, [left, right])

    def test_len(self):
        for rg in all_ranges():
            s = set(rg)
            assert_less_equal(len(s), len(rg), [rg, s])

        for left, right in all_pairs():
            if len(set(left)) == len(set(right)):
                assert_equal(len(left), len(right), [left, right])
            else:
                assert_not_equal(len(left), (right), [left, right])

    def test_lessequal_true(self):
        for rg in all_ranges():
            assert_less_equal(set(rg), set(rg), rg)
            assert_less_equal(set(rg), rg, rg)
            assert_less_equal(rg, set(rg), rg)
            assert_less_equal(rg, rg, rg)

    def test_lessequal_others(self):
        for left, right in all_pairs():
            if set(left) <= set(right):
                assert_less_equal(left, right, [left, right])
                assert_less_equal(set(left), right, [left, right])
                assert_less_equal(left, set(right), [left, right])
            else:
                assert not left <= right, [left, right]
                assert not left <= set(right), [left, right]
                assert not set(left) <= right, [left, right]

            if set(right) <= set(left):
                assert_less_equal(right, left, [right, left])
                assert_less_equal(set(right), left, [right, left])
                assert_less_equal(right, set(left), [right, left])
            else:
                assert not right <= left, [right, left]
                assert not right <= set(left), [right, left]
                assert not set(right) <= left, [right, left]

    def test_intersection(self):
        for left, right in all_pairs():
            assert_equal(set(left) & set(right),
                         set(left & right),
                         [left, right, left & right])
            assert_equal(set(left) & set(right),
                         set(right & left),
                         [left, right, left & right])

            assert_equal(set(left) & set(right),
                         set(left) & right,
                         [left, right, left & right])
            assert_equal(set(left) & set(right),
                         left & set(right),
                         [left, right, left & right])

    def test_disjoint(self):
        for left, right in all_pairs():
            assert_equal(set(left).isdisjoint(set(right)),
                         left.isdisjoint(right),
                         [left, right, left & right])
            assert_equal(set(left).isdisjoint(set(right)),
                         right.isdisjoint(left),
                         [left, right, left & right])

            assert_equal(set(left).isdisjoint(set(right)),
                         set(left).isdisjoint(right),
                         [left, right, left & right])
            assert_equal(set(left).isdisjoint(set(right)),
                         left.isdisjoint(set(right)),
                         [left, right, left & right])

    def test_union(self):
        for left, right in all_pairs():
            assert_equal(set(left) | set(right),
                         set(left | right),
                         [left, right, left | right])
            assert_equal(set(left) | set(right),
                         set(right | left),
                         [left, right, left | right])

            assert_equal(set(left) | set(right),
                         set(left) | right,
                         [left, right, left | right])
            assert_equal(set(left) | set(right),
                         left | set(right),
                         [left, right, left | right])

    def test_sub(self):
        for left, right in all_pairs():
            assert_equal(set(left) - set(right),
                         set(left - right),
                         [left, right, left - right])
            assert_equal(set(right) - set(left),
                         set(right - left),
                         [left, right, right - left])

            assert_equal(set(left) - set(right),
                         set(left) - right,
                         [left, right, left - right])
            assert_equal(set(left) - set(right),
                         left - set(right),
                         [left, right, left - right])

            assert_equal(set(right) - set(left),
                         set(right) - left,
                         [left, right, right - left])
            assert_equal(set(right) - set(left),
                         right - set(left),
                         [left, right, right - left])

    def test_block_intersection(self):
        for left, right in all_pairs():
            if left and left.value_type is str:
                continue
            if right and right.value_type is str:
                continue
            assert_equal(set(iterblocks(
                                intersect_many(left.to_blocks(),
                                               right.to_blocks()))),
                         left & right,
                         [left, right, left & right])

            assert_equal(set(iterblocks(
                                intersect_many(right.to_blocks(),
                                               left.to_blocks()))),
                         left & right,
                         [left, right, left & right])

    def test_blocks_len(self):
        for rg in all_ranges():
            if rg and rg.value_type is str:
                continue
            blocks = rg.to_blocks()
            assert_less_equal(len(rg), blockslen(blocks), [rg, blocks])

    def test_plain_block_intersection(self):
        for left, right in all_pairs():
            if left and left.value_type is str:
                continue
            if right and right.value_type is str:
                continue
            assert_equal(set(iterblocks(
                                intersect_many(left.to_plain_blocks(),
                                               right.to_plain_blocks()))),
                         left & right,
                         [left, right, left & right])

            assert_equal(set(iterblocks(
                                intersect_many(right.to_plain_blocks(),
                                               left.to_plain_blocks()))),
                         left & right,
                         [left, right, left & right])

    def test_plain_blocks_len(self):
        for rg in all_ranges():
            if rg and rg.value_type is str:
                continue
            blocks = rg.to_plain_blocks()
            assert_less_equal(len(rg), blockslen(blocks), [rg, blocks])
