# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:13:51 2021

@author: chris.kerklaan
"""
# Third-party imports
from osgeo import ogr

# Local imports
from .geometry import Geometry

# Globals
POINT_COVERAGE = [
    ogr.wkbPoint,
    ogr.wkbPoint25D,
    ogr.wkbPointM,
    ogr.wkbPointZM,
]
MULTIPOINT_COVERAGE = [
    ogr.wkbMultiPoint,
    ogr.wkbMultiPoint25D,
    ogr.wkbMultiPointM,
    ogr.wkbMultiPointZM,
]


class Point(Geometry):
    ogr_coverage = POINT_COVERAGE

    def __init__(self, geometry: ogr.wkbPoint = None):
        super().__init__(geometry, ogr.wkbPoint)
        self.check_type(Point.ogr_coverage)

    @classmethod
    def from_point(cls, points: tuple = None, flatten=True):
        """takes tuple points and creates an ogr point"""
        output_geom = ogr.Geometry(ogr.wkbPoint)
        output_geom.AddPoint(*points)

        if flatten:
            output_geom.FlattenTo2D()

        return cls(output_geom)

    @property
    def point(self):
        return self.points[0]


class MultiPoint(Geometry):
    ogr_coverage = MULTIPOINT_COVERAGE

    def __init__(self, geometry: ogr.wkbMultiPoint):
        super().__init__(geometry, ogr.wkbMultiPoint)

        if self.type == ogr.wkbPoint:
            raise TypeError(
                """geometry is multi while vector is single
                                use vector.to_single()
                            """
            )
        self.check_type(MultiPoint.ogr_coverage)

    @classmethod
    def from_points(cls, points, flatten=True):
        """takes list of tuple points and creates an ogr multipoint"""
        output_geom = ogr.Geometry(ogr.wkbMultiPoint)
        for point in points:
            point_geometry = ogr.Geometry(ogr.wkbPoint)
            point_geometry.AddPoint(*point)
            output_geom.AddGeometry(point_geometry)

        if flatten:
            output_geom.FlattenTo2D()

        return cls(output_geom)

    @property
    def points_geometry(self):
        return [Point(point) for point in self]

    @property
    def points(self):
        return [point.GetPoint() for point in self]
