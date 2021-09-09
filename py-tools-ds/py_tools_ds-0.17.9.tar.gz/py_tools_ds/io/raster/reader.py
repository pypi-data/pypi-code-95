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

import multiprocessing
import ctypes
import numpy as np
from osgeo import gdal

from ...numeric.array import get_array_tilebounds

__author__ = "Daniel Scheffler"


shared_array = None


def init_SharedArray_in_globals(dims):
    rows, cols = dims
    global shared_array
    shared_array_base = multiprocessing.Array(ctypes.c_double, rows * cols)
    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.reshape(rows, cols)


def fill_arr(argDict, def_param=shared_array):
    pos = argDict.get('pos')
    func = argDict.get('func2call')
    args = argDict.get('func_args', [])
    kwargs = argDict.get('func_kwargs', {})

    (rS, rE), (cS, cE) = pos
    shared_array[rS:rE + 1, cS:cE + 1] = func(*args, **kwargs)


def gdal_read_subset(fPath, pos, bandNr):
    (rS, rE), (cS, cE) = pos
    ds = gdal.Open(fPath)
    data = ds.GetRasterBand(bandNr).ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
    del ds
    return data


def gdal_ReadAsArray_mp(fPath, bandNr, tilesize=1500):
    ds = gdal.Open(fPath)
    rows, cols = ds.RasterYSize, ds.RasterXSize
    del ds

    init_SharedArray_in_globals((rows, cols))

    tilepos = get_array_tilebounds(array_shape=(rows, cols), tile_shape=[tilesize, tilesize])
    fill_arr_argDicts = [{'pos': pos, 'func2call': gdal_read_subset, 'func_args': (fPath, pos, bandNr)} for pos in
                         tilepos]

    with multiprocessing.Pool() as pool:
        pool.map(fill_arr, fill_arr_argDicts)

    return shared_array
