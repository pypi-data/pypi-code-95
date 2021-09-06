# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 14:14:17 2021

@author: chris.kerklaan
"""
# First-party import
import math
import logging

# Third-party imports
import numpy as np
from osgeo import ogr

# Local imports
from .geometry import Geometry
from .point import Point, MultiPoint

# Globals
LINESTRING_COVERAGE = [
    ogr.wkbLineString,
    ogr.wkbLineString25D,
    ogr.wkbLineStringM,
    ogr.wkbLineStringZM,
]
MULTILINESTRING_COVERAGE = [
    ogr.wkbMultiLineString,
    ogr.wkbMultiLineString25D,
    ogr.wkbMultiLineStringM,
    ogr.wkbMultiLineStringZM,
]


# Logger
logger = logging.getLogger(__name__)


class LineString(Geometry):

    ogr_coverage = LINESTRING_COVERAGE

    def __init__(self, geometry: ogr.wkbLineString = None):
        super().__init__(geometry, ogr.wkbLineString)
        self.check_type(LineString.ogr_coverage)

    @classmethod
    def from_points(cls, points, flatten=True):
        """takes list of tuple points and creates an ogr linestring"""
        output_geom = ogr.Geometry(ogr.wkbLineString)
        for point in points:
            output_geom.AddPoint(*point)
        if flatten:
            output_geom.FlattenTo2D()
        return cls(output_geom)

    def __iter__(self):
        """iterates over the vertices"""
        points = self.points
        for pid in range(0, len(points) - 1):
            yield LineString.from_points([points[pid], points[pid + 1]])

    @property
    def points_geometry(self):
        return [Point.from_point(point) for point in self.points]

    @property
    def start_point(self):
        return self.points_geometry[0]

    @property
    def end_point(self):
        return self.points_geometry[-1]

    def middle_point(self, interval=1):
        points = self.points_on_line(interval, vertices=True)
        return points[int(len(points) / 2)]

    def reversed(self):
        """reverses the line"""
        points = self.points
        points.reverse()
        return LineString.from_points(points)

    def intersection(self, geometry):
        """intersection of a linestring, returns a point, multipoint or none"""
        if self.Intersects(geometry):
            intersection = self.Intersection(geometry)

            if intersection.GetGeometryType() == ogr.wkbPoint:
                return Point(intersection)
            elif intersection.GetGeometryType() == ogr.wkbLineString:
                return LineString(intersection)
            else:
                return MultiPoint(intersection)

        else:
            logger.debug("Found no intersection")
            return None

    def points_on_line(
        self,
        interval=1,
        custom_interval=None,
        start=True,
        end=True,
        vertices=False,
        geometry=True,
    ):
        """Return points on a linestring

        Params:
            interval: distance between poitns
            custom_interval: a list of distances
            start: include start point
            end: include end point
            vertices: include vertices
            geometry: returns as a point
        """

        return points_on_line(
            self.points,
            interval,
            custom_interval,
            start,
            end,
            vertices,
            geometry,
        )

    def perpendicular_lines(
        self,
        distance,
        perpendicular_length,
        start=True,
        end=True,
        vertices=False,
    ):

        """returns a perpendicular linestring on point1 with a certain dist
        params:
            distance: distance between perpendicular lines
            perpendicular_length: length of the lines
        """
        return perpendicular_lines(
            self,
            distance,
            perpendicular_length,
            start=start,
            end=end,
            vertices=vertices,
        )

    def add_vertice(self, geometry: Point, snapping_size=0.000000001):
        """returns a linestring with an extra vertice on the point
        If the vertice is already present, we will not adjust it.

        most likely there are two types of linestrings
        1. With one coordinate
        2. With a connection between coordinates
        this add vertice is for assumption 1.

        """
        points = []
        snap_count = 0
        for vertice in self:
            vertice_point = vertice.points[0]
            if vertice_point not in points:
                points.append(vertice_point)

            if vertice.Intersects(geometry.Buffer(snapping_size)):
                if geometry.point not in points:
                    points.append(geometry.point)

                snap_count += 1

        # last one
        if vertice.points[-1] not in points:
            points.append(vertice.points[-1])

        if snap_count == 0:
            logger.debug("snap not found")

        return LineString.from_points(points)

    def split_on_vertices(self):
        return [vertice for vertice in self]

    def as_multi(self):
        return MultiLineString.from_points(self.points)

    def transform(self, epsg):
        return LineString(self.reproject(epsg))


class MultiLineString(Geometry):

    ogr_coverage = MULTILINESTRING_COVERAGE

    def __init__(self, geometry: ogr.wkbMultiLineString = None):
        super().__init__(geometry, ogr.wkbMultiLineString)

        if self.type == ogr.wkbLineString:
            raise TypeError(
                """geometry is multi while vector is single
                                use vector.to_single()
                            """
            )
        self.check_type(MultiLineString.ogr_coverage)

    @classmethod
    def from_points(cls, points, flatten=True):
        """creates a ogr multilinestring from points"""

        output_geom = ogr.Geometry(ogr.wkbMultiLineString)

        # check if input is a single linestring
        if type(points[0]) == tuple:
            points = [[point] for point in points]

        for point in points:
            line = ogr.Geometry(ogr.wkbLineString)
            for p in point:
                line.AddPoint(*p)
            output_geom.AddGeometry(line)

        if flatten:
            output_geom.FlattenTo2D()

        return cls(output_geom)


def calc_dist(x1, y1, x2, y2):
    """returns the distance beteen two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def lower_bound(x, l):
    if l[0] > x and not l[0] == x:
        return
    for i, y in enumerate(l):
        if y > x:
            return l[i - 1]


def points_with_distance(point1, point2, distance):
    """
    Returns a point on a certain distance between two points
    Note that the distance is the distance from the first point in the coordinate unit
    """
    t = distance / calc_dist(*point1, *point2)
    p = (
        ((1 - t) * point1[0] + t * point2[0]),
        ((1 - t) * point1[1] + t * point2[1]),
    )

    if type(p[0]) is np.ndarray:
        return t, (p[0][0], p[1][0])
    else:
        return t, p


def points_on_line(
    points,
    interval=1,
    custom_interval: list = None,
    start=True,
    end=True,
    vertices=False,
    geometry=True,
):
    """
    returns a point on the line for every interval that is given
    use combine to also include begin, endpoint and vertices
    Params:
        interval: distance between poitns
        custom_interval: a list of distances
        start: include start point
        end: include end point
        vertices: include vertices
        geometry: returns as a point
    """

    sections = list(
        np.cumsum(
            [
                calc_dist(*points[pid], *points[pid + 1])
                for pid in range(0, len(points) - 1)
            ]
        )
    )
    total_dist = sections[-1]

    if custom_interval is not None:
        new_sections = custom_interval
    else:
        new_sections = np.linspace(interval, total_dist, int(total_dist / interval))

    if vertices:
        new_sections = sorted(list(new_sections) + sections)

    new_points = []
    for i in new_sections:
        bound = lower_bound(i, sections)
        if not bound:
            index = 0
            dist = i
        else:
            index = sections.index(bound) + 1
            dist = i - sections[sections.index(bound)]

        ratio, point = points_with_distance(
            points[index], points[index + 1], distance=dist
        )

        if 0 <= ratio <= 1:
            new_points.append(point)
        else:
            pass

    if start:
        new_points.insert(0, points[0])

    if end:
        new_points.append(points[-1])

    if geometry:
        return [Point.from_point(point) for point in new_points]

    return new_points


def angle(pt1, pt2):
    x_diff = pt2[0] - pt1[0]
    y_diff = pt2[1] - pt1[1]
    return math.degrees(math.atan2(y_diff, x_diff))


def perpendicular_points(pt, bearing, dist):
    """returns perpendicular points at point"""
    bearing_pt1 = math.radians(bearing + 90)
    bearing_pt2 = math.radians(bearing - 90)
    points = []
    for bearing in [bearing_pt1, bearing_pt2]:
        x = pt[0] + dist * math.cos(bearing)
        y = pt[1] + dist * math.sin(bearing)
        points.append((x, y))
    return points


def perpendicular_line(pt1, pt2, dist):
    return LineString.from_points(perpendicular_points(pt1, angle(pt1, pt2), dist))


def perpendicular_lines(
    linestring,
    line_dist=10,
    perp_dist=10,
    start=True,
    end=True,
    vertices=False,
):
    """returns perpendicular lines on a linestring"""
    points = linestring.points_on_line(
        interval=line_dist,
        custom_interval=None,
        start=start,
        end=end,
        vertices=vertices,
        geometry=False,
    )

    lines = [
        perpendicular_line(points[index], points[index + 1], perp_dist)
        for index in range(0, len(points) - 1)
    ]

    # add last point
    if len(points) > 1:
        lines.append(perpendicular_line(points[-1], points[-2], perp_dist))

    return lines
