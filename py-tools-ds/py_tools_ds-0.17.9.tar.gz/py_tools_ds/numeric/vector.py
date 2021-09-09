# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2016-2021  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import collections
import numpy as np
import bisect
from typing import Iterable  # noqa F401  # flake8 issue

__author__ = "Daniel Scheffler"


def find_nearest(array, value, roundAlg='auto', extrapolate=False, exclude_val=False, tolerance=0):
    # type: (Iterable, float, str, bool, bool, float) -> float
    """Find the value of an array nearest to a another single value.

    NOTE: In case of extrapolation an EQUALLY INCREMENTED array (like a coordinate grid) is assumed!

    :param array:       array or list of numbers
    :param value:       a number
    :param roundAlg:    <str> 'auto', 'on', 'off'
    :param extrapolate: extrapolate the given array if the given value is outside the array
    :param exclude_val: exclude the given value from possible return values
    :param tolerance:   tolerance (with array = [10, 20, 30] and value=19.9 and roundAlg='off' and tolerance=0.1, 20
                                   is returned)
    """
    assert roundAlg in ['auto', 'on', 'off']
    assert isinstance(array, list) or (isinstance(array, np.ndarray) and len(array.shape) == 1)
    array = sorted(list(array))

    if exclude_val and value in array:
        array.remove(value)

    if extrapolate:
        increment = abs(array[1] - array[0])
        if value > max(array):  # expand array until value
            array = np.arange(min(array), value + 2 * increment, increment)  # 2 * inc to make array_sub work below
        if value < min(array):  # negatively expand array until value
            array = (np.arange(max(array), value - 2 * increment, -increment))[::-1]
    elif value < min(array) or value > max(array):
        raise ValueError('Value %s is outside of the given array.' % value)

    if roundAlg == 'auto':
        diffs = np.abs(np.array(array) - value)
        minDiff = diffs.min()
        minIdx = diffs.argmin()
        isMiddleVal = collections.Counter(diffs)[minDiff] > 1  # value exactly between its both neighbours
        idx = minIdx if not isMiddleVal else bisect.bisect_left(array, value)
        out = array[idx]
    elif roundAlg == 'off':
        idx = bisect.bisect_left(array, value)
        if array[idx] == value:
            out = value  # exact hit
        else:
            idx -= 1
            out = array[idx]  # round off
    else:  # roundAlg == 'on'
        idx = bisect.bisect_left(array, value)
        out = array[idx]

    if tolerance:
        array_sub = array[idx - 1: idx + 2]
        diffs = np.abs(np.array(array_sub) - value)
        inTol = diffs <= tolerance

        if True in inTol:
            out = array_sub[np.argwhere(inTol.astype(int) == 1)[0][0]]

    return out
