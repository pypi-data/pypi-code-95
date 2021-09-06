# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 13:49:48 2021

@author: chris.kerklaan

Wrapper for an ogr geometry

TODO:
    1. Convert/fix geometry should have an input geom_type and a target_geom_type
    2. Geometry testing

"""
# First-party imports
import logging

# Third-party imports
from osgeo import ogr

# Local imports
from .spatial_reference import SpatialReference


# GLOBALS
logger = logging.getLogger(__name__)

POLYGON = "POLYGON (({x1} {y1},{x2} {y1},{x2} {y2},{x1} {y2},{x1} {y1}))"
POINT = "POINT ({x1} {y1})"
LINESTRING = "LINESTRING ({x1} {y1}, {x2} {y2})"

TRANSLATION = {
    "point": ogr.wkbPoint,
    "line": ogr.wkbLineString,
    "polygon": ogr.wkbPolygon,
    "multipoint": ogr.wkbMultiPoint,
    "multiline": ogr.wkbMultiLineString,
    "multiPolygon": ogr.wkbMultiPolygon,
}

SINGLE_TYPES = {
    6: 3,
    5: 2,
    4: 1,
    3: 3,
    2: 2,
    1: 1,
}  # polygon  # linestring  # point

MULTI_TYPES = {
    1: 4,
    2: 5,
    3: 6,
    4: 4,
    5: 5,
    6: 6,
}

SINGLE_TYPES_INVERT = dict(map(reversed, SINGLE_TYPES.items()))
SINGLE_TO_MULTIPLE = {1: [1, 4], 2: [2, 5], 3: [3, 6], 4: [4], 5: [5], 6: [6]}


class Geometry(ogr.Geometry):
    """
    Extension of an ogr geometry

    Copies the input of a geomtry, hence the pointer connection is lost
    and geometries must be set via set_feature

    Every function always leaves the original geometry untouched

    Geometry is fixed as much as possible

    """

    def __init__(self, geometry, geometry_type=ogr.wkbPoint):
        geometry, _ = fix(geometry, target_geom_type=geometry_type)
        super().__init__(wkb=geometry.ExportToWkb())
        self.AssignSpatialReference(geometry.GetSpatialReference())

    def check_type(self, types):
        if not self.type in types:
            raise TypeError(f"Wrong ogr geom type {self.name} {self.type_name}")

    @property
    def area(self):
        return self.GetArea()

    @property
    def length(self):
        return self.Length()

    @property
    def name(self):
        return self.GetGeometryName()

    @property
    def type(self):
        return self.GetGeometryType()

    @property
    def type_name(self):
        return ogr.GeometryTypeToName(self.type)

    @property
    def valid(self):
        return self.IsValid()

    @property
    def fixed(self):
        return fix(self)

    @property
    def points(self):
        return self.GetPoints()

    @property
    def envelope(self):
        return self.GetEnvelope()

    @property
    def wkt(self):
        return self.ExportToWkt()

    @property
    def wkb(self):
        return self.ExportToWkb()

    @property
    def wkb_size(self):
        return self.WkbSize()

    @property
    def point_on_surface(self):
        return Geometry(self.PointOnSurface())

    @property
    def centroid(self):
        return Geometry(self.Centroid())

    @property
    def spatial_reference(self):
        return SpatialReference.from_sr(self.GetSpatialReference(), self.centroid)

    @spatial_reference.setter
    def spatial_reference(self, sr_input):
        """takes an epsg or a spatial_reference input"""
        if type(sr_input) == int:
            sr_input = SpatialReference.from_epsg(sr_input)
        self.AssignSpatialReference(sr_input)

    @property
    def epsg(self):
        return self.spatial_reference.epsg

    @property
    def ogr(self):
        """returns a pure ogr geometry"""
        return release(self)

    def copy(self):
        return Geometry(geometry=self)

    def buffer(self, size):
        return Geometry(self.Buffer(size))

    def simplify(self, simplification):
        return Geometry(self.Simplify(simplification))

    def difference(self, geometry):
        """returns a differenced geometry, or none if invalid or not intersects"""
        return Geometry(difference(self, geometry))

    def clip(self, mask):
        """returns a list of clipped geometry in the correct output type
        or none
        """
        clipped = clip(self, mask, self.type)
        if clipped:
            return [Geometry(i) for i in clipped]
        else:
            return

    def reproject(self, out_epsg):
        """returns a reprojected geometry
        gives an error, dont know why
        """
        geometry = self.ogr
        transform = self.spatial_reference.transform(out_epsg)

        geometry.Transform(transform)
        return Geometry(geometry, self.type)

    def dissolve(self):
        """dissolved geometry, returns a single geometry"""
        return Geometry(dissolve(self))

    def to_single(self):
        """creates single parts, returns a list or none"""
        return [Geometry(i) for i in multipart_to_singlepart(self)]


def release(geometry: ogr.Geometry):
    """releases the c pointer from the geometry"""
    output = ogr.CreateGeometryFromWkb(geometry.ExportToWkb())
    output.AssignSpatialReference(geometry.GetSpatialReference())
    return output


def convert_geometry(geometry, target_geom_type):
    """
    converts geometry to target type to it's logical output type
    if ambiguous output type, it is converted to target_geom_type
    e.g., when it is a geometry collection
    """
    geom_type = geometry.GetGeometryType()
    if geom_type == target_geom_type:
        return geometry

    if geom_type in [
        ogr.wkbCurvePolygon,
        ogr.wkbCurvePolygonM,
        ogr.wkbCurvePolygonZ,
        ogr.wkbCurvePolygonZM,
    ]:
        geometry = geometry.GetLinearGeometry()  # to polygon

    elif geom_type in [
        ogr.wkbMultiSurface,
        ogr.wkbMultiSurfaceM,
        ogr.wkbMultiSurfaceZ,
        ogr.wkbMultiSurfaceZM,
    ]:
        geometry = ogr.ForceToMultiPolygon(geometry)  # multi
    elif geom_type in [
        ogr.wkbGeometryCollection,
        ogr.wkbGeometryCollection25D,
        ogr.wkbGeometryCollectionM,
        ogr.wkbGeometryCollectionZM,
    ]:
        logger.debug("Found a geometry collection, setting to target geometry")
        for geom in geometry:
            if geom.GetGeometryType() == target_geom_type:
                geometry = geom
                break

    return geometry


def fix(geometry, target_geom_type=None):
    """
    First converts a geometry to type 1,2,3,4,5,6
    Fixes a geometry to ogr geom types 1,2,3,4,5,6:
        1. pointcount for  linestrings
        2. self intersections for polygons
        3. 3D polygon

    if a geometry collection is given, it can convert to a geom_type by
    setting target_geom_type = something

    Params:
        geometry : ogr geometry
        target_geom_type: = None, fixes it until this geometry type
    Returns
        geometry: ogr geometry or None if no geometry is present
        bool: geometry validity


    """
    if geometry is None:
        return None, False

    if not target_geom_type:
        target_geom_type = geometry.GetGeometryType()

    geometry = convert_geometry(geometry, target_geom_type)

    if geometry.IsValid():
        return geometry, True

    # Transforms multipolugon into geometry collection
    # geometry = geometry.MakeValid()
    # if geometry.IsValid():
    # return geometry, True

    geom_type = geometry.GetGeometryType()
    if geom_type == ogr.wkbPoint:
        pass

    elif geom_type == ogr.wkbLineString:
        if geometry.GetPointCount() == 1:
            logger.debug("Geometry point count of linestring = 1")
            return geometry, False

    elif geom_type == ogr.wkbPolygon:
        geometry = geometry.Buffer(0)

    elif geom_type == ogr.wkbMultiPoint:
        pass

    elif geom_type == ogr.wkbMultiLineString:
        pass

    elif geom_type == ogr.wkbMultiPolygon:
        geometry = geometry.Buffer(0)

    geom_type = geometry.GetGeometryType()
    geom_name = ogr.GeometryTypeToName(geom_type)

    if geometry.Is3D():
        geometry.FlattenTo2D()

    if not geometry.IsValid():
        raise ValueError()
        logger.warning(
            f"failed fix invalid ogr geometry type: {geom_name}, {geom_type}, target {target_geom_type} "
        )
    return geometry, geometry.IsValid()


def multipart_to_singlepart(geometry: ogr.Geometry):
    """returns a list of geometries, if invalid none"""
    geometry, valid = fix(geometry)

    if not valid:
        logger.debug("Invalid geometry")
        return

    if "MULTI" in geometry.GetGeometryName():

        # release geometry from pointer
        return [release(part) for part in geometry]
    else:
        return [geometry]


def clip(geometry: ogr.Geometry, mask: ogr.Geometry, output_type: int):
    """Clips a single geometry on a mask
    returns in valid geoms as none
    returns a geometry of the output type
    returns a list
    """
    geometry, valid = fix(geometry)
    if not valid:
        logger.debug("Invalid geometry")
        return

    if geometry.Intersects(mask.Boundary()):
        intersect = geometry.Intersection(mask)
        intersect_type = intersect.GetGeometryType()
        if intersect_type not in SINGLE_TO_MULTIPLE[output_type]:
            logger.debug("Output has incorrect geometry type")
            return

        if intersect_type > 3:
            return [intersect]
        else:
            return multipart_to_singlepart(intersect)

    elif geometry.Within(mask):
        return [geometry]
    else:
        return  # outside


def difference(geometry: ogr.Geometry, mask: ogr.Geometry):
    """checks if intersects or valid before doing difference"""
    geometry, valid = fix(geometry)
    if not valid:
        logger.debug("Invalid geometry")
        return

    if not geometry.Intersects(mask):
        return

    if geometry.Intersects(mask):
        geometry = geometry.Difference(mask)

    return geometry


def dissolve(multigeometry: ogr.Geometry):
    """dissolves a multigeometry into a single geometry"""
    multigeometry, valid = fix(multigeometry)
    if not valid:
        logger.debug("Invalid geometry")
        return

    geometry_type = multigeometry.GetGeometryType()
    if geometry_type == ogr.wkbMultiPolygon:
        union = multigeometry.UnionCascaded()
    else:
        union = ogr.Geometry(geometry_type)
        for geometry in multigeometry:
            union = union.Union(geometry)
    return union
