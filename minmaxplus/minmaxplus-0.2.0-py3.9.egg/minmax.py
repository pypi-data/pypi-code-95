#! /usr/bin/python3
# -*- coding: utf-8 -*-

#############################################################################
# MinMax+  extends builtin min and max functions.
# Copyright (C) 2021 alexpdev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
############################################################################

"""
Functions that provide a more robust way obtain min and max.

Potential replacement function for the builtin min and max functions.
Returns the expected value as well as the values index within the sequence.
Only works on iterables that are indexed i.e. tuple or list.
"""

import sys


class InputError(Exception):
    """Input Type is not an iterable sequence."""

    def __init__(self, value):
        message = "Input type cannot be indexed"
        super().__init__(message)

class EmptySequenceError(Exception):
    """Input iterable is empty."""

    def __init__(self, value):
        message = "Input iterable is empty."
        super().__init__(message)

def maxp(seq):
    """Get array element and index with maximum value.

    Args:
        seq list/tuple: any indexed iterable sequence

    Returns:
        tuple[any, int] : (max_value, max_index)
    """
    if len(seq) == 0:
        raise EmptySequenceError
    if not hasattr(seq, "index"):
        raise InputError
    max_, max_i, n = -sys.maxsize, 0, len(seq)
    # checks if seq length is odd
    if n & 1:
        n -= 1
    for i in range(0, n, 2):
        if seq[i + 1] > seq[i]:
            maximum, index = seq[i + 1], i + 1
        else:
            maximum, index = seq[i], i
        if maximum > max_:
            max_, max_i = maximum, index
    # checks if seq length is odd
    if len(seq) & 1:
        if seq[n] > max_:
            max_, max_i = seq[n], n
    return (max_, max_i)


def minp(seq):
    """Get array element and index with maximum value.

    Args:
        list/tuple: any indexed iterable sequence.

    Returns:
        tuple[any,int]: (min_value, min_index)
    """
    if not hasattr(seq, "index"):
        raise InputError
    if len(seq) == 0:
        raise EmptySequenceError
    min_, min_i, n = sys.maxsize, 0, len(seq)
    # checks if seq length is odd
    if n & 1:
        n -= 1
    for i in range(0, n, 2):
        if seq[i + 1] < seq[i]:
            minimum, index = seq[i + 1], i + 1
        else:
            minimum, index = seq[i], i
        if minimum < min_:
            min_, min_i = minimum, index
    # checks if seq length is odd
    if len(seq) & 1:
        if seq[n] < min_:
            min_, min_i = seq[n], n
    return (min_, min_i)


def minmax(seq):
    """Get value and index of maximum element and minimum elements in array.

    Args:
        arr ([list/tuple]): Any indexed iterable

    Returns:
        list[tuple[any, int], tuple[any, int]]: [(max_value,max_index),(min_value,min_index)]
    """
    if not hasattr(seq, "index"):
        raise InputError
    if len(seq) == 0:
        raise EmptySequenceError
    max_, max_i, n = -sys.maxsize, 0, len(seq)
    min_, min_i = sys.maxsize, 0
    # checks if seq length is odd
    if n & 1:
        n -= 1
    for i in range(0, n, 2):
        if seq[i + 1] > seq[i]:
            maximum, maxindex = seq[i + 1], i + 1
            minimum, minindex = seq[i], i
        else:
            minimum, minindex = seq[i + 1], i + 1
            maximum, maxindex = seq[i], i
        if maximum > max_:
            max_, max_i = maximum, maxindex
        if minimum < min_:
            min_, min_i = minimum, minindex
    # checks if seq length is odd
    if len(seq) & 1:
        if seq[n] > max_:
            max_, max_i = seq[n], n
        if seq[n] < min_:
            min_, min_i = seq[n], n
    return [(min_, min_i), (max_, max_i)]
