#
# Geos Accessor for Series
#
from math import sin, cos, tan
import numpy as np
import pandas as pd
import pygeos
from ._array import GeosArray
from ._delegated_series import (
    get_SeriesProperty,
    get_IndexedSeriesProperty,
    get_IndexedDataFrameProperty,
    get_ReturnMethodUnary,
    get_NoneMethodUnary,
    # get_SeriesMethodUnary,
    get_IndexedSeriesMethodUnary,
    # get_IndexedDataFrameMethodUnary,
    get_MethodBinary,
    enableDataFrameExpand,
)

try:
    import geopandas as gpd
except ImportError:
    gpd = None


__all__ = ['GeosSeriesAccessor']


@pd.api.extensions.register_series_accessor('geos')
class GeosSeriesAccessor:
    """
    Access PyGEOS functionality through the "geos" series accessor keyword.

    Example:
        >>> s = pd.Series(pygeos.points(range(15), 0), dtype='geos')
        >>> s
        0    POINT (0 0)
        1    POINT (1 0)
        2    POINT (2 0)
        3    POINT (3 0)
        4    POINT (4 0)
        5    POINT (5 0)
        6    POINT (6 0)
        7    POINT (7 0)
        8    POINT (8 0)
        9    POINT (9 0)
        dtype: geos
        >>> s.geos.has_z
        0    False
        1    False
        2    False
        3    False
        4    False
        5    False
        6    False
        7    False
        8    False
        9    False
        Name: has_z, dtype: bool
    """
    def __init__(self, obj):
        if gpd is not None and pd.api.types.pandas_dtype('geometry') == obj.dtype:
            obj = pd.Series(GeosArray(obj.array.data), name=obj.name)
        elif (pd.api.types.pandas_dtype('geos') != obj.dtype):
            raise AttributeError(f'Cannot use "geos" accessor on objects of dtype "{obj.dtype}"')
        self._obj = obj

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    def from_geopandas(self, copy=False):
        """
        Transform a :class:`geopandas.GeoSeries` into a regular Series with a geos dtype.

        Args:
            copy (bool, optional): Whether to copy the data or return a wrapper around the same data; Default **False**

        Returns:
            pandas.Series: Series with a geos dtype.
        """
        if copy:
            return self._obj.copy()
        else:
            return self._obj

    def to_geopandas(self, crs=None, copy=False):
        """
        Convert a geos Series into a :class:`geopandas.GeoSeries`.

        Args:
            crs (any, optional): CRS to use with GeoPandas, check the docs for more information; Default **None**
            copy (bool, optional): Whether to copy the data or return a wrapper around the same data; Default **False**

        Returns:
            geopandas.GeoSeries: The geopandas series.

        Raises:
            ImportError: Geopandas is not installed.
            AttributeError: Series is not of geos dtype.
        """
        if gpd is None:
            raise ImportError('Geopandas is required for this function')

        if isinstance(self._obj, gpd.GeoSeries):
            s = self._obj
        else:
            s = gpd.GeoSeries(self._obj.astype(object), crs=crs)

        if copy:
            return s.copy()
        else:
            return s

    # -------------------------------------------------------------------------
    # Geometry
    # -------------------------------------------------------------------------
    get_coordinate_dimension = get_IndexedSeriesProperty('geometry.get_coordinate_dimension')
    get_dimensions = get_IndexedSeriesProperty('geometry.get_dimensions')
    get_exterior_ring = get_IndexedSeriesProperty('geometry.get_exterior_ring', geos=True)
    get_interior_ring = get_IndexedSeriesMethodUnary('geometry.get_interior_ring', geos=True)
    get_num_coordinates = get_IndexedSeriesProperty('geometry.get_num_coordinates')
    get_num_geometries = get_IndexedSeriesProperty('geometry.get_num_geometries')
    get_num_interior_rings = get_IndexedSeriesProperty('geometry.get_num_interior_rings')
    get_num_points = get_IndexedSeriesProperty('geometry.get_num_points')
    get_parts = get_SeriesProperty('geometry.get_parts', geos=True)
    get_point = get_IndexedSeriesMethodUnary('geometry.get_point', geos=True)
    get_precision = get_IndexedSeriesProperty('geometry.get_precision')
    get_srid = get_IndexedSeriesProperty('geometry.get_srid')
    get_type_id = get_IndexedSeriesProperty('geometry.get_type_id')
    get_x = get_IndexedSeriesProperty('geometry.get_x')
    get_y = get_IndexedSeriesProperty('geometry.get_y')
    get_z = get_IndexedSeriesProperty('geometry.get_z')
    set_precision = get_NoneMethodUnary('geometry.set_precision')
    set_srid = get_NoneMethodUnary('geometry.set_srid')

    # -------------------------------------------------------------------------
    # Geometry Creation
    # -------------------------------------------------------------------------
    destroy_prepared = get_NoneMethodUnary('creation.destroy_prepared')
    prepare = get_NoneMethodUnary('creation.prepare')

    # -------------------------------------------------------------------------
    # Measurement
    # -------------------------------------------------------------------------
    area = get_IndexedSeriesProperty('measurement.area')
    bounds = get_IndexedDataFrameProperty('measurement.bounds', ['xmin', 'ymin', 'xmax', 'ymax'])
    distance = get_MethodBinary('measurement.distance')
    frechet_distance = get_MethodBinary('measurement.frechet_distance')
    hausdorff_distance = get_MethodBinary('measurement.hausdorff_distance')
    length = get_IndexedSeriesProperty('measurement.length')
    minimum_bounding_radius = get_IndexedSeriesProperty('measurement.minimum_bounding_radius')
    minimum_clearance = get_IndexedSeriesProperty('measurement.minimum_clearance')
    total_bounds = get_SeriesProperty('measurement.total_bounds', ['xmin', 'ymin', 'xmax', 'ymax'])

    # -------------------------------------------------------------------------
    # Predicates
    # -------------------------------------------------------------------------
    contains = get_MethodBinary('predicates.contains')
    contains_properly = get_MethodBinary('predicates.contains_properly')
    covered_by = get_MethodBinary('predicates.covered_by')
    covers = get_MethodBinary('predicates.covers')
    crosses = get_MethodBinary('predicates.crosses')
    disjoint = get_MethodBinary('predicates.disjoint')
    equals = get_MethodBinary('predicates.equals')
    equals_exact = get_MethodBinary('predicates.equals_exact')
    has_z = get_IndexedSeriesProperty('predicates.has_z')
    intersects = get_MethodBinary('predicates.intersects')
    is_ccw = get_IndexedSeriesProperty('predicates.is_ccw')
    is_closed = get_IndexedSeriesProperty('predicates.is_closed')
    is_empty = get_IndexedSeriesProperty('predicates.is_empty')
    is_geometry = get_IndexedSeriesProperty('predicates.is_geometry')
    is_missing = get_IndexedSeriesProperty('predicates.is_missing')
    is_prepared = get_IndexedSeriesProperty('predicates.is_prepared')
    is_ring = get_IndexedSeriesProperty('predicates.is_ring')
    is_simple = get_IndexedSeriesProperty('predicates.is_simple')
    is_valid = get_IndexedSeriesProperty('predicates.is_valid')
    is_valid_input = get_IndexedSeriesProperty('predicates.is_valid_input')
    is_valid_reason = get_IndexedSeriesProperty('predicates.is_valid_reason')
    overlaps = get_MethodBinary('predicates.overlaps')
    relate = get_MethodBinary('predicates.relate')
    relate_pattern = get_MethodBinary('predicates.relate_pattern')
    touches = get_MethodBinary('predicates.touches')
    within = get_MethodBinary('predicates.within')

    # -------------------------------------------------------------------------
    # Set operations
    # -------------------------------------------------------------------------
    coverage_union = get_MethodBinary('set_operations.coverage_union', geos=True)
    coverage_union_all = get_ReturnMethodUnary('set_operations.coverage_union_all')
    difference = get_MethodBinary('set_operations.difference', geos=True)
    intersection = get_MethodBinary('set_operations.intersection', geos=True)
    intersection_all = get_ReturnMethodUnary('set_operations.intersection_all')
    symmetric_difference = get_MethodBinary('set_operations.symmetric_difference', geos=True)
    symmetric_difference_all = get_ReturnMethodUnary('set_operations.symmetric_difference_all')
    union = get_MethodBinary('set_operations.union', geos=True)
    union_all = get_ReturnMethodUnary('set_operations.union_all')

    # -------------------------------------------------------------------------
    # Constructive operations
    # -------------------------------------------------------------------------
    boundary = get_IndexedSeriesProperty('constructive.boundary', geos=True)
    buffer = get_IndexedSeriesMethodUnary('constructive.buffer', geos=True)
    build_area = get_ReturnMethodUnary('constructive.build_area')
    centroid = get_IndexedSeriesProperty('constructive.centroid', geos=True)
    clip_by_rect = get_IndexedSeriesMethodUnary('constructive.clip_by_rect', geos=True)
    convex_hull = get_IndexedSeriesProperty('constructive.convex_hull', geos=True)
    delaunay_triangles = get_IndexedSeriesMethodUnary('constructive.delaunay_triangles', geos=True)
    envelope = get_IndexedSeriesProperty('constructive.envelope', geos=True)
    extract_unique_points = get_IndexedSeriesProperty('constructive.extract_unique_points', geos=True)
    make_valid = get_IndexedSeriesProperty('constructive.make_valid', geos=True)
    minimum_bounding_circle = get_IndexedSeriesProperty('constructive.minimum_bounding_circle', geos=True)
    minimum_rotated_rectangle = get_IndexedSeriesProperty('constructive.minimum_rotated_rectangle', geos=True)
    normalize = get_IndexedSeriesProperty('constructive.normalize', geos=True)
    offset_curve = get_IndexedSeriesMethodUnary('constructive.offset_curve', geos=True)
    oriented_envelope = get_IndexedSeriesProperty('constructive.oriented_envelope', geos=True)
    point_on_surface = get_IndexedSeriesProperty('constructive.point_on_surface', geos=True)
    polygonize = get_ReturnMethodUnary('constructive.polygonize')
    reverse = get_IndexedSeriesProperty('constructive.reverse', geos=True)
    segmentize = get_ReturnMethodUnary('constructive.segmentize')
    simplify = get_IndexedSeriesMethodUnary('constructive.simplify', geos=True)
    snap = get_IndexedSeriesMethodUnary('constructive.snap', geos=True)
    voronoi_polygons = get_IndexedSeriesMethodUnary('constructive.voronoi_polygons', geos=True)

    # -------------------------------------------------------------------------
    # Linestring operations
    # -------------------------------------------------------------------------
    line_interpolate_point = get_IndexedSeriesMethodUnary('linear.line_interpolate_point', geos=True)
    line_locate_point = get_IndexedSeriesMethodUnary('linear.line_locate_point', geos=True)
    line_merge = get_IndexedSeriesProperty('linear.line_merge', geos=True)
    shared_paths = get_MethodBinary('linear.shared_paths', geos=True)
    shortest_line = get_MethodBinary('linear.shortest_line', geos=True)

    # -------------------------------------------------------------------------
    # Coordinate operations
    # -------------------------------------------------------------------------
    apply = get_IndexedSeriesMethodUnary('coordinates.apply', geos=True)
    count_coordinates = get_IndexedSeriesProperty('coordinates.count_coordinates')
    get_coordinates = get_ReturnMethodUnary('coordinates.get_coordinates')
    set_coordinates = get_IndexedSeriesMethodUnary('coordinates.set_coordinates', geos=True)

    # -------------------------------------------------------------------------
    # STRTree
    # -------------------------------------------------------------------------
    STRtree = get_ReturnMethodUnary('strtree.STRtree')

    # -------------------------------------------------------------------------
    # Custom Methods
    # -------------------------------------------------------------------------
    @enableDataFrameExpand
    def affine(self, matrix):
        r"""
        Performs a 2D or 3D affine transformation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                =
                \begin{bmatrix}
                    a & b & x_{off} \\
                    d & e & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                =
                \begin{bmatrix}
                    a & b & c & x_{off} \\
                    d & e & f & y_{off} \\
                    g & h & i & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}

        Args:
            matrix (numpy.ndarray or list-like): Affine transformation matrix.

        Returns:
            pandas.Series: Transformed geometries.

        Note:
            The transformation matrix can be one of the following types:

            - numpy.ndarray <3x3 or 2x3> |br|
              Performs a 2D affine transformation, where the last row of homogeneous coordinates can optionally be discarded.
            - list-like <6> |br|
              Performs a 2D affine transformation, where the `matrix` represents **(a, b, d, e, xoff, yoff)**.
            - numpy.ndarray <4x4 or 3x4> |br|
              Performs a 3D affine transformation, where the last row of homogeneous coordinates can optionally be discarded.
            - list-like <12> |br|
              Performs a 3D affine transformation, where the `matrix` represents **(a, b, c, d, e, f, g, h, i, xoff, yoff, zoff)**.
        """
        result = self._obj.array.affine(matrix)
        return pd.Series(result, index=self._obj.index, name='affine')

    @enableDataFrameExpand
    def rotate(self, *angles, origin):
        r"""
        Performs a 2D or 3D rotation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    cos(a) & -sin(a) & x_{off} \\
                    sin(a) & cos(a)  & y_{off} \\
                    0      & 0       & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - x_{origin}*cos(a) + y_{origin}*sin(a) \\
                y_{off} &= y_{origin} - x_{origin}*sin(a) - y_{origin}*cos(a)

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    cos(a_z)*cos(a_y) &
                    cos(a_z)*sin(a_y)*sin(a_x) - sin(a_z)*cos(a_x) &
                    cos(a_z)*sin(a_y)*cos(a_x) + sin(a_z)*sin(a_x) &
                    x_{off} \\
                    sin(a_z)*cos(a_y) &
                    sin(a_z)*sin(a_y)*sin(a_x) + cos(a_z)*cos(a_x) &
                    sin(a_z)*sin(a_y)*cos(a_x) - cos(a_z)*sin(a_x) &
                    y_{off} \\
                    -sin(a_y) &
                    cos(a_y)*sin(a_x) &
                    cos(a_y)*cos(a_x) &
                    z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - (a)*x_{origin} - (b)*y_{origin} - (c)*z_{origin} \\
                y_{off} &= y_{origin} - (d)*x_{origin} - (e)*y_{origin} - (f)*z_{origin} \\
                z_{off} &= z_{origin} - (g)*x_{origin} - (h)*y_{origin} - (i)*z_{origin}

        Args:
            angles (float): 2D rotation angle or X,Y,Z 3D rotation angles in radians.
            origin (pygeos.lib.Geometry or list-like): Origin point for the transformation.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if origin is None:
            origin = (0, 0, 0)
        elif isinstance(origin, pygeos.lib.Geometry):
            if pygeos.get_type_id(origin) != 0:
                raise TypeError('Origin should be a single point geometry')
            origin = np.nan_to_num(pygeos.get_coordinates(origin, True)).squeeze()

        if len(angles) == 1:
            x0, y0 = origin[:2]
            ca = cos(angles[0])
            sa = sin(angles[0])
            result = self._obj.array.affine((
                ca, -sa,
                sa, ca,
                x0 - x0*ca + y0*sa,
                y0 - x0*sa - y0*ca,
            ))
        elif len(angles) == 3:
            x0, y0, z0 = origin[:3]
            cx, cy, cz = (cos(a) for a in angles)
            sx, sy, sz = (sin(a) for a in angles)
            a = cz*cy
            b = cz*sy*sx - sz*cx
            c = cz*sy*cx + sz*sx
            d = sz*cy
            e = sz*sy*sx + cz*cx
            f = sz*sy*cx - cz*sx
            g = -sy
            h = cy*sx
            i = cy*cx
            result = self._obj.array.affine((
                a, b, c,
                d, e, f,
                g, h, i,
                x0 - a*x0 - b*y0 - c*z0,
                y0 - d*x0 - e*y0 - f*z0,
                z0 - g*x0 - h*y0 - i*z0,
            ))
        else:
            raise ValueError('The rotate transformation requires 1 or 3 angles')

        return pd.Series(result, index=self._obj.index, name='rotate')

    @enableDataFrameExpand
    def scale(self, x, y, z=None, *, origin=None):
        r"""
        Performs a 2D or 3D scaling on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    x_s & 0 & x_{off} \\
                    0 & y_s & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - x_{origin}*x_s \\
                y_{off} &= y_{origin} - y_{origin}*y_s

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    x_s & 0 & 0 & x_{off} \\
                    0 & y_s & 0 & y_{off} \\
                    0 & 0 & z_s & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}
                \\
                x_{off} &= x_{origin} - x_{origin}*x_s \\
                y_{off} &= y_{origin} - y_{origin}*y_s \\
                z_{off} &= z_{origin} - z_{origin}*z_s

        Args:
            x (float): Scaling value in the X direction.
            y (float): Scaling value in the Y direction.
            z (float, optional): Scaling value in the Z direction; Default **None**.
            origin (pygeos.lib.Geometry or list-like): Origin point for the transformation.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if origin is None:
            origin = (0, 0, 0)
        elif isinstance(origin, pygeos.lib.Geometry):
            if pygeos.get_type_id(origin) != 0:
                raise TypeError('Origin should be a single point geometry')
            origin = np.nan_to_num(pygeos.get_coordinates(origin, True)).squeeze()

        if z is None:
            x0, y0 = origin[:2]
            result = self._obj.array.affine((
                x, 0,
                0, y,
                x0 - x * x0,
                y0 - y * y0,
            ))
        else:
            x0, y0, z0 = origin[:3]
            result = self._obj.array.affine((
                x, 0, 0,
                0, y, 0,
                0, 0, z,
                x0 - x * x0,
                y0 - y * y0,
                z0 - z * z0,
            ))

        return pd.Series(result, index=self._obj.index, name='scale')

    @enableDataFrameExpand
    def skew(self, *angles, origin=None):
        r"""
        Performs a 2D or 3D skew/shear transformation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & a_{xy} & x_{off} \\
                    a_{yx} & 1 & y_{off} \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}
                \\
                x_{off} &= -(y_{origin}*a_{xy}) \\
                y_{off} &= -(x_{origin}*a_{yx})

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & a_{xy} & a_{xz} & x_{off} \\
                    a_{yx} & 1 & a_{yz} & y_{off} \\
                    a_{zx} & a_{zy} & 1 & z_{off} \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}
                \\
                x_{off} &= -(y_{origin}*a_{xy} + z_{origin}*a_{xz}) \\
                y_{off} &= -(x_{origin}*a_{yx} + z_{origin}*a_{yz}) \\
                z_{off} &= -(x_{origin}*a_{zx} + y_{origin}*a_{zy})

        Args:
            angles (float): skewing angles (2D: ``[x, y]`` ; 3D: ``[xy, xz, yx, yz, zx, zy]``)
            origin (pygeos.lib.Geometry or list-like): Origin point for the transformation.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if origin is None:
            origin = (0, 0, 0)
        elif isinstance(origin, pygeos.lib.Geometry):
            if pygeos.get_type_id(origin) != 0:
                raise TypeError('Origin should be a single point geometry')
            origin = np.nan_to_num(pygeos.get_coordinates(origin, True)).squeeze()

        if len(angles) == 2:
            x0, y0 = origin[:2]
            x, y = (tan(a) for a in angles)
            result = self._obj.array.affine((
                1, x,
                y, 1,
                -(y0*x),
                -(x0*y),
            ))
        elif len(angles) == 6:
            x0, y0, z0 = origin[:3]
            xy, xz, yx, yz, zx, zy = (tan(a) for a in angles)
            result = self._obj.array.affine((
                1, xy, xz,
                yx, 1, yz,
                zx, zy, 1,
                -(y0*xy + z0*xz),
                -(x0*yx + z0*yz),
                -(x0*zx + y0*zy),
            ))
        else:
            raise ValueError('The skew transformation requires 2 or 6 angles')

        return pd.Series(result, index=self._obj.index, name='skew')

    @enableDataFrameExpand
    def translate(self, x, y, z=None):
        r"""
        Performs a 2D or 3D translation on all the coordinates.

        2D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & 0 & x_t \\
                    0 & 1 & y_t \\
                    0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ 1
                \end{bmatrix}

        3D
            .. math::

                \begin{bmatrix}
                    x' \\ y' \\ z' \\ 1
                \end{bmatrix}
                &=
                \begin{bmatrix}
                    1 & 0 & 0 & x_t \\
                    0 & 1 & 0 & y_t \\
                    0 & 0 & 1 & z_t \\
                    0 & 0 & 0 & 1 \\
                \end{bmatrix}
                \begin{bmatrix}
                    x \\ y \\ z \\ 1
                \end{bmatrix}

        Args:
            x (float): Translation value in the X direction.
            y (float): Translation value in the Y direction.
            z (float, optional): Translation value in the Z direction; Default **None**.

        Returns:
            pandas.Series: Transformed geometries.
        """
        if z is None:
            result = self._obj.array.affine((1, 0, 0, 1, x, y))
        else:
            result = self._obj.array.affine((1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z))

        return pd.Series(result, index=self._obj.index, name='translate')

    @enableDataFrameExpand
    def apply_shapely(self, func):
        """
        Applies a function to each geometry as a shapely object.

        Args:
            func (callable): Function that gets a shapely geometry and should return a shapely geometry or None

        Returns:
            pandas.Series: Transformed geometries.

        Note:
            This function is supposed to be used when some functionality from is missing from PyGEOS,
            but is available in shapely.
            However, do note that it is very inneficient.

            1. Transform array to shapely.
            2. Loop over list and apply function.
            3. Transform list of shapely to GeosArray.
            4. Return Series.
        """
        result = GeosArray.from_shapely([func(geom) for geom in self._obj.array.to_shapely()])
        return pd.Series(result, index=self._obj.index, name='shapely')
