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

import numpy as np

# custom
from shapely.geometry import shape, mapping, box
from shapely.geometry import Polygon  # noqa F401  # flake8 issue
from shapely import wkt
from pyproj import CRS
from osgeo import gdal, ogr, osr

from ..coord_trafo import imYX2mapYX, mapYX2imYX, pixelToMapYX
from ...dtypes.conversion import get_dtypeStr, dTypeDic_NumPy2GDAL

__author__ = "Daniel Scheffler"


def shapelyImPoly_to_shapelyMapPoly_withPRJ(shapelyImPoly, gt, prj):
    # ACTUALLY PRJ IS NOT NEEDED BUT THIS FUNCTION RETURNS OTHER VALUES THAN shapelyImPoly_to_shapelyMapPoly
    geojson = mapping(shapelyImPoly)
    coords = list(geojson['coordinates'][0])
    coordsYX = pixelToMapYX(coords, geotransform=gt, projection=prj)
    coordsXY = tuple([(i[1], i[0]) for i in coordsYX])
    geojson['coordinates'] = (coordsXY,)
    return shape(geojson)


def shapelyImPoly_to_shapelyMapPoly(shapelyBox, gt):
    xmin, ymin, xmax, ymax = shapelyBox.bounds
    ymax, xmin = imYX2mapYX((ymax, xmin), gt)
    ymin, xmax = imYX2mapYX((ymin, xmax), gt)
    return box(xmin, ymin, xmax, ymax)


def shapelyBox2BoxYX(shapelyBox, coord_type='image'):
    xmin, ymin, xmax, ymax = shapelyBox.bounds
    assert coord_type in ['image', 'map']

    if coord_type == 'image':
        UL_YX = ymin, xmin
        UR_YX = ymin, xmax
        LR_YX = ymax, xmax
        LL_YX = ymax, xmin
    else:
        UL_YX = ymax, xmin
        UR_YX = ymax, xmax
        LR_YX = ymin, xmax
        LL_YX = ymin, xmin

    return UL_YX, UR_YX, LR_YX, LL_YX


def get_boxImXY_from_shapelyPoly(shapelyPoly, im_gt):
    # type: (Polygon, tuple) -> list
    """Convert each vertex coordinate of a shapely polygon into image coordinates corresponding to the given
    geotransform without respect to invalid image coordinates. Those must be filtered later.

    :param shapelyPoly:     <shapely.Polygon>
    :param im_gt:           <list> the GDAL geotransform of the target image
    """
    def get_coordsArr(shpPoly): return np.swapaxes(np.array(shpPoly.exterior.coords.xy), 0, 1)
    coordsArr = get_coordsArr(shapelyPoly)
    boxImXY = [mapYX2imYX((Y, X), im_gt) for X, Y in coordsArr.tolist()]  # FIXME incompatible to GMS version
    boxImXY = [(i[1], i[0]) for i in boxImXY]
    return boxImXY


def round_shapelyPoly_coords(shapelyPoly, precision=10):
    # type: (Polygon, int) -> Polygon
    """Round the coordinates of the given shapely polygon.

    :param shapelyPoly:     the shapely polygone
    :param precision:       number of decimals
    :return:
    """
    return wkt.loads(wkt.dumps(shapelyPoly, rounding_precision=precision))


def points_to_raster(points, values, tgt_res, prj=None, fillVal=None):
    # type: (np.ndarray, np.ndarray, float, str, float) -> (np.ndarray, list, str)
    """
    Convert a set of point geometries with associated values into a raster array.

    :param points: list or 1D numpy.ndarray containings shapely.geometry point geometries
    :param values: list or 1D numpy.ndarray containing int or float values
    :param tgt_res: target resolution in projection units
    :param prj: WKT projection string
    :param fillVal: fill value used to fill in where no point geometry is available
    """
    ds = ogr.GetDriverByName("Memory").CreateDataSource('wrk')

    if prj is not None:
        if int(gdal.__version__[0]) < 3:
            # noinspection PyTypeChecker
            prj = CRS(prj).to_wkt(version="WKT1_GDAL")

        srs = osr.SpatialReference()
        srs.ImportFromWkt(prj)
    else:
        srs = None

    layer = ds.CreateLayer('', srs, ogr.wkbPoint)

    # create field
    DTypeStr = get_dtypeStr(values if isinstance(values, np.ndarray) else values[0])
    FieldType = ogr.OFTInteger if DTypeStr.startswith('int') else ogr.OFTReal
    FieldDefn = ogr.FieldDefn('VAL', FieldType)
    if DTypeStr.startswith('float'):
        FieldDefn.SetPrecision(6)
    layer.CreateField(FieldDefn)  # Add one attribute

    for i in range(len(points)):
        # Create a new feature (attribute and geometry)
        feat = ogr.Feature(layer.GetLayerDefn())
        feat.SetGeometry(ogr.CreateGeometryFromWkb(points[i].wkb))  # Make a geometry, from Shapely object
        feat.SetField('VAL', values[i])

        layer.CreateFeature(feat)
        feat.Destroy()

    x_min, x_max, y_min, y_max = layer.GetExtent()

    # Create the destination data source
    cols = int((x_max - x_min) / tgt_res)
    rows = int((y_max - y_min) / tgt_res)
    target_ds = gdal.GetDriverByName('MEM').Create('raster', cols, rows, 1, dTypeDic_NumPy2GDAL[DTypeStr])
    target_ds.SetGeoTransform((x_min, tgt_res, 0, y_max, 0, -tgt_res))
    target_ds.SetProjection(prj if prj else '')
    band = target_ds.GetRasterBand(1)
    if fillVal is not None:
        band.Fill(fillVal)
    band.FlushCache()

    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], layer, options=["ATTRIBUTE=VAL"])

    out_arr = target_ds.GetRasterBand(1).ReadAsArray()
    out_gt = target_ds.GetGeoTransform()
    out_prj = target_ds.GetProjection()

    del target_ds, ds, layer, band

    return out_arr, out_gt, out_prj
