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

__author__ = "Daniel Scheffler"

import numpy as np
from typing import List, Iterable  # noqa F401  # flake8 issue


def get_outFillZeroSaturated(dtype) -> tuple:
    """Return proper 'fill-', 'zero-' and 'saturated' values with respect to the given data type.

    :param dtype: data type
    """
    dtype = str(np.dtype(dtype))
    assert dtype in ['int8', 'uint8', 'int16', 'uint16', 'float32'], \
        "get_outFillZeroSaturated: Unknown dType: '%s'." % dtype
    dict_outFill = {'int8': -128, 'uint8': 0, 'int16': -9999, 'uint16': 9999, 'float32': -9999.}
    dict_outZero = {'int8': 0, 'uint8': 1, 'int16': 0, 'uint16': 1, 'float32': 0.}
    dict_outSaturated = {'int8': 127, 'uint8': 256, 'int16': 32767, 'uint16': 65535, 'float32': 65535.}

    return dict_outFill[dtype], dict_outZero[dtype], dict_outSaturated[dtype]


def get_array_tilebounds(array_shape, tile_shape):
    # type: (Iterable, Iterable) -> List[List[tuple]]
    """Calculate row/col bounds for image tiles according to the given parameters.

    :param array_shape:    dimensions of array to be tiled: (rows, columns, bands) or (rows, columns)
    :param tile_shape:     dimensions of target tile: (rows, columns, bands) or (rows, columns)
    """
    rows, cols = array_shape[:2]
    tgt_rows, tgt_cols = tile_shape[:2]
    tgt_rows, tgt_cols = tgt_rows or rows, tgt_cols or cols  # return all rows/cols in case tile_shape contains None

    row_bounds = [0]
    while row_bounds[-1] + tgt_rows < rows:
        row_bounds.append(row_bounds[-1] + tgt_rows - 1)
        row_bounds.append(row_bounds[-2] + tgt_rows)
    else:
        row_bounds.append(rows - 1)

    col_bounds = [0]
    while col_bounds[-1] + tgt_cols < cols:
        col_bounds.append(col_bounds[-1] + tgt_cols - 1)
        col_bounds.append(col_bounds[-2] + tgt_cols)
    else:
        col_bounds.append(cols - 1)

    return [[tuple([row_bounds[r], row_bounds[r + 1]]), tuple([col_bounds[c], col_bounds[c + 1]])]
            for r in range(0, len(row_bounds), 2) for c in range(0, len(col_bounds), 2)]
