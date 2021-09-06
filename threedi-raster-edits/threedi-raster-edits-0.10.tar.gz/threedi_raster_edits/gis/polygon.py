# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:14:38 2021

@author: chris.kerklaan
"""
# First-party imports
import logging

# Third-party imports
from osgeo import ogr

# Local imports
from .geometry import Geometry

# GLOBALS
logger = logging.getLogger(__name__)

POLYGON_COVERAGE = [
    ogr.wkbPolygon,
    ogr.wkbPolygon25D,
    ogr.wkbPolygonM,
    ogr.wkbPolygonZM,
    ogr.wkbCurvePolygon,
    ogr.wkbCurvePolygonM,
    ogr.wkbCurvePolygonZ,
    ogr.wkbCurvePolygonZM,
]

MULTIPOLYGON_COVERAGE = [
    ogr.wkbMultiPolygon,
    ogr.wkbMultiPolygon25D,
    ogr.wkbMultiPolygonM,
    ogr.wkbMultiPolygonZM,
    ogr.wkbMultiSurface,
    ogr.wkbMultiSurface,
    ogr.wkbMultiSurfaceM,
    ogr.wkbMultiSurfaceZ,
    ogr.wkbMultiSurfaceZM,
]


class Polygon(Geometry):
    ogr_coverage = POLYGON_COVERAGE

    def __init__(self, geometry: ogr.wkbPolygon = None):
        super().__init__(geometry, ogr.wkbPolygon)
        self.check_type(Polygon.ogr_coverage)

    @classmethod
    def from_points(cls, points, flatten=True, close=True):
        """takes list of tuple points and creates an ogr polygon"""

        output_geom = ogr.Geometry(ogr.wkbPolygon)

        ring = ogr.Geometry(ogr.wkbLinearRing)
        for point in points:
            ring.AddPoint(*point)

        output_geom.AddGeometry(ring)

        if close:
            output_geom.CloseRings()

        if flatten:
            output_geom.FlattenTo2D()

        if not output_geom.IsValid():
            logger.warning(
                """
                            Is it a self-intersection polygon?
                            Are the points in the form a ring? E.g., 
                            left-upper, left-lower, right-lower, right-upper"""
            )

        return cls(output_geom)


class MultiPolygon(Geometry):
    ogr_coverage = MULTIPOLYGON_COVERAGE

    def __init__(self, geometry: ogr.wkbMultiPolygon = None, points: list = None):

        if points:
            geometry = self.create_multipolygon(points)
        super().__init__(geometry, ogr.wkbMultiPolygon)

        # check types
        if self.type == ogr.wkbPolygon:
            raise TypeError(
                """geometry is multi while vector is single
                                use vector.to_single()
                            """
            )
        self.check_type(MultiPolygon.ogr_coverage)

    @classmethod
    def from_points(cls, points, flatten=True, close=True):
        output_geom = ogr.Geometry(ogr.wkbMultiPolygon)

        for point in points:
            ring = ogr.Geometry(ogr.wkbLinearRing)
            for p in point:
                ring.AddPoint(p)

            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)
            output_geom.AddGeometry(poly)

        if close:
            output_geom.CloseRings()

        if flatten:
            output_geom.FlattenTo2D()

        if not output_geom.IsValid():
            logger.warning(
                """
                            Is it a self-intersection polygon?
                            Are the points in the form a ring? E.g., 
                            left-upper, left-lower, right-lower, right-upper"""
            )
        return cls(output_geom)


def union(geometries, geom_type=ogr.wkbMultiPolygon):
    """create an union for multiple polygons"""

    multi = ogr.Geometry(geom_type)
    for geometry in geometries:
        multi.AddGeometryDirectly(geometry)
    return ogr.ForceTo(multi.UnionCascaded().Clone(), 3)
