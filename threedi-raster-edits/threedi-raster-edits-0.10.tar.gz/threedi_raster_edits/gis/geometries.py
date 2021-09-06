# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:42:15 2021

@author: chris.kerklaan
"""
# Third-party imports
from osgeo import ogr

# Local imports
from .point import Point, MultiPoint
from .linestring import LineString, MultiLineString
from .polygon import Polygon, MultiPolygon

# Globals
GEOMETRIES = [
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
]
OGR_GEOMETRY_CONVERSION = {}
for geometry in GEOMETRIES:
    OGR_GEOMETRY_CONVERSION.update(
        {coverage: geometry for coverage in geometry.ogr_coverage}
    )


def geometry_type_class(ogr_geometry_type):
    """returns the correct geometry type given an ogr_geometry"""
    try:
        geometry_class = OGR_GEOMETRY_CONVERSION[ogr_geometry_type]
    except KeyError:
        name = ogr.GeometryTypeToName(ogr_geometry_type)
        raise ValueError(f"Found unexpected geometry type {name}")
    else:
        return geometry_class


def convert_geometry(geometry: ogr.Geometry):
    """converts an ogr geometry to the custom ogr geometry classes"""
    return geometry_type_class(geometry.GetGeometryType())(geometry)
