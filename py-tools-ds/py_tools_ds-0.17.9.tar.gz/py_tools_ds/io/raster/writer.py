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

import os
import multiprocessing

from pyproj import CRS
from osgeo import gdal

from ...dtypes.conversion import convertGdalNumpyDataType
from ...geo.map_info import geotransform2mapinfo
from ...numeric.array import get_array_tilebounds

__author__ = "Daniel Scheffler"


def write_numpy_to_image(array, path_out, outFmt='GTIFF', gt=None, prj=None):
    rows, cols, bands = list(array.shape) + [1] if len(array.shape) == 2 else array.shape
    gdal_dtype = gdal.GetDataTypeByName(convertGdalNumpyDataType(array.dtype))
    outDs = gdal.GetDriverByName(outFmt).Create(path_out, cols, rows, bands, gdal_dtype)
    for b in range(bands):
        band = outDs.GetRasterBand(b + 1)
        arr2write = array if len(array.shape) == 2 else array[:, :, b]
        band.WriteArray(arr2write)
        del band
    if gt:
        outDs.SetGeoTransform(gt)
    if prj:
        if int(gdal.__version__[0]) < 3:
            # noinspection PyTypeChecker
            prj = CRS(prj).to_wkt(version="WKT1_GDAL")

        outDs.SetProjection(prj)
    del outDs


def write_envi(arr, outpath, gt=None, prj=None):
    from spectral.io import envi

    if gt or prj:
        assert gt and prj, 'gt and prj must be provided together or left out.'

    meta = {'map info': geotransform2mapinfo(gt, prj), 'coordinate system string': prj} if gt else None
    shape = (arr.shape[0], arr.shape[1], 1) if len(arr.shape) == 3 else arr.shape
    out = envi.create_image(outpath, metadata=meta, shape=shape, dtype=arr.dtype, interleave='bsq', ext='.bsq',
                            force=True)  # 8bit for multiple masks in one file
    out_mm = out.open_memmap(writable=True)
    out_mm[:, :, 0] = arr


shared_array_on_disk__memmap = None


def init_SharedArray_on_disk(out_path, dims, gt=None, prj=None):
    from spectral.io import envi

    global shared_array_on_disk__memmap
    global shared_array_on_disk__path
    path = out_path if not os.path.splitext(out_path)[1] == '.bsq' else \
        os.path.splitext(out_path)[0] + '.hdr'
    Meta = {}
    if gt and prj:
        Meta['map info'] = geotransform2mapinfo(gt, prj)
        Meta['coordinate system string'] = prj
    shared_array_on_disk__obj = envi.create_image(path, metadata=Meta, shape=dims, dtype='uint16',
                                                  interleave='bsq', ext='.bsq', force=True)
    shared_array_on_disk__memmap = shared_array_on_disk__obj.open_memmap(writable=True)


def fill_arr_on_disk(argDict):
    pos = argDict.get('pos')
    in_path = argDict.get('in_path')
    band = argDict.get('band')

    (rS, rE), (cS, cE) = pos
    ds = gdal.Open(in_path)
    band = ds.GetRasterBand(band)
    data = band.ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
    shared_array_on_disk__memmap[rS:rE + 1, cS:cE + 1, 0] = data
    del ds, band


def convert_gdal_to_bsq__mp(in_path, out_path, band=1):
    """

    Usage:
        ref_ds,tgt_ds = gdal.Open(self.path_imref),gdal.Open(self.path_im2shift)
        ref_pathTmp, tgt_pathTmp = None,None
        if ref_ds.GetDriver().ShortName!='ENVI':
            ref_pathTmp = IO.get_tempfile(ext='.bsq')
            IO.convert_gdal_to_bsq__mp(self.path_imref,ref_pathTmp)
            self.path_imref = ref_pathTmp
        if tgt_ds.GetDriver().ShortName!='ENVI':
            tgt_pathTmp = IO.get_tempfile(ext='.bsq')
            IO.convert_gdal_to_bsq__mp(self.path_im2shift,tgt_pathTmp)
            self.path_im2shift = tgt_pathTmp
        ref_ds=tgt_ds=None

    :param in_path:
    :param out_path:
    :param band:
    :return:
    """

    ds = gdal.Open(in_path)
    dims = (ds.RasterYSize, ds.RasterXSize)
    gt, prj = ds.GetGeoTransform(), ds.GetProjection()
    del ds
    init_SharedArray_on_disk(out_path, dims, gt, prj)
    positions = get_array_tilebounds(array_shape=dims, tile_shape=[512, 512])

    argDicts = [{'pos': pos, 'in_path': in_path, 'band': band} for pos in positions]

    with multiprocessing.Pool() as pool:
        pool.map(fill_arr_on_disk, argDicts)
