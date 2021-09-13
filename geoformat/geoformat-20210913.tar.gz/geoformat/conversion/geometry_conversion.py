import copy

try:
    from osgeo import ogr
    from osgeo import osr
    import_ogr_success = True
except ImportError:
    import_ogr_success = False

import time
import geoformat

from geoformat.conversion.bbox_conversion import bbox_extent_to_2d_bbox_extent
from geoformat.conversion.coordinates_conversion import coordinates_to_2d_coordinates, format_coordinates

from geoformat.conf.geometry_variable import GEOMETRY_CODE_TO_GEOMETRY_TYPE
from geoformat.conversion.bytes_conversion import big_endian_wkb_geometry_type_to_geometry_type, \
    geometry_type_to_wkb_geometry_type, int_to_4_bytes_integer, coordinates_list_to_bytes, integer_4_bytes_to_int, \
    double_8_bytes_to_float
from geoformat.geoprocessing.connectors.operations import coordinates_to_bbox
from geoformat.geoprocessing.geoparameters.bbox import bbox_union
from geoformat.geoprocessing.geoparameters.boundaries import ccw_or_cw_boundary

from geoformat.conf.error_messages import import_ogr_error

geometry_type_to_dimension = {
    'Point': 2,
    'LineString': 2,
    'Polygon': 2,
    'MultiPoint': 2,
    'MultiLineString': 2,
    'MultiPolygon': 2,
}

geometry_type_to_upper_case = {
    'Point': 'POINT',
    'LineString': 'LINESTRING',
    'Polygon': 'POLYGON',
    'MultiPoint': 'MULTIPOINT',
    'MultiLineString': 'MULTILINESTRING',
    'MultiPolygon': 'MULTIPOLYGON',
    'GeometryCollection': 'GEOMETRYCOLLECTION'
}
upper_case_to_geometry_type = {
    'POINT': 'Point',
    'LINESTRING': 'LineString',
    'POLYGON': 'Polygon',
    'MULTIPOINT': 'MultiPoint',
    'MULTILINESTRING': 'MultiLineString',
    'MULTIPOLYGON': 'MultiPolygon',
    'GEOMETRYCOLLECTION': 'GeometryCollection'
}


def geometry_type_to_2d_geometry_type(geometry_type):
    """Convert xD geometry type to 2D geometry type

    :param geometry_type
    :return 2d geometry type
    """
    if 'POINT' in geometry_type.upper():
        new_geometry_type = 'Point'
    elif 'LINESTRING' in geometry_type.upper():
        new_geometry_type = 'LineString'
    elif 'POLYGON' in geometry_type.upper():
        new_geometry_type = 'Polygon'
    elif 'GEOMETRYCOLLECTION' in geometry_type.upper():
        new_geometry_type = 'GeometryCollection'
    else:
        raise Exception("Geometry type unknown")

    if 'MULTI' in geometry_type.upper():
        new_geometry_type = 'Multi' + new_geometry_type

    return new_geometry_type


def geometry_to_2d_geometry(geometry, bbox=True):
    """
    Convert a geometry with 2 or more dimension to 2d dimension geometry.

    :param geometry: input geometry with 2 or more dimension
    :param bbox: boolean that indicate if we want or not the bbox information in geometry
    :return new geometry with 2 dimensions
    """
    geometry_collection = geometry_to_geometry_collection(geometry, bbox=bbox)

    for i_geom, geom in enumerate(geometry_collection['geometries']):
        new_geometry_type = geometry_type_to_2d_geometry_type(geom['type'])
        new_geometry = {'type': new_geometry_type, 'coordinates': coordinates_to_2d_coordinates(geom['coordinates'])}
        if bbox:
            if 'bbox' in geom:
                bbox = bbox_extent_to_2d_bbox_extent(geom['bbox'])
            else:
                bbox = coordinates_to_bbox(new_geometry['coordinates'])

            new_geometry['bbox'] = bbox

        geometry_collection['geometries'][i_geom] = new_geometry

    if geometry['type'].upper() == 'GEOMETRYCOLLECTION':
        return geometry_collection
    else:
        return geometry_collection['geometries'][0]


def geometry_to_geometry_collection(geometry, geometry_type_filter=None, bbox=True):
    """
    Transform a geometry to GeometryCollection
    """
    if geometry_type_filter:
        if isinstance(geometry_type_filter, str):
            geometry_type_filter = {geometry_type_filter}
        elif isinstance(geometry_type_filter, (list, tuple, set)):
            geometry_type_filter = set(geometry_type_filter)
        else:
            raise Exception('geometry_type_filter must be a geometry type or a list of geometry type')

    geometry_type = geometry['type']
    # if input geometry is not an geometry collection
    if geometry_type != 'GeometryCollection':
        geometry_in_collection = copy.deepcopy(geometry)
        if geometry_type_filter:
            if geometry_type in geometry_type_filter:
                geometry_collection = {'type': 'GeometryCollection', 'geometries': [geometry_in_collection]}
            else:
                geometry_collection = {'type': 'GeometryCollection', 'geometries': []}
        else:
            geometry_collection = {'type': 'GeometryCollection', 'geometries': [geometry_in_collection]}

        if bbox and geometry['coordinates']:
            if 'bbox' in geometry:
                bbox = geometry['bbox']
            else:
                bbox = coordinates_to_bbox(geometry['coordinates'])
                geometry_in_collection['bbox'] = bbox
            geometry_collection['bbox'] = bbox

    # if input geometry is a geometry collection
    else:
        # if geometry is not empty
        if geometry['geometries']:
            if bbox:
                bbox_geometry_collection = None

            geometry_list = [None] * len(geometry['geometries'])
            del_idx = []
            for i_geom, geometry in enumerate(geometry['geometries']):
                geometry_in_collection = copy.deepcopy(geometry)
                write_geometry = True
                if geometry_type_filter:
                    if geometry['type'] not in geometry_type_filter:
                        write_geometry = False
                else:
                    if bbox:
                        if 'bbox' not in geometry:
                            bbox_geometry = coordinates_to_bbox(geometry_in_collection['coordinates'])

                            if not bbox_geometry_collection and bbox_geometry:
                                bbox_geometry_collection = bbox_geometry
                            else:
                                bbox_geometry_collection = bbox_union(bbox_geometry, bbox_geometry_collection)

                            if bbox and bbox_geometry:
                                geometry_in_collection['bbox'] = bbox_geometry

                # write geometry in list
                if write_geometry:
                    geometry_list[i_geom] = geometry_in_collection
                else:
                    del_idx.append(i_geom)

            # delete filter geometries
            if del_idx:
                for idx in reversed(del_idx):
                    del geometry_list[idx]

            geometry_collection = {'type': 'GeometryCollection', 'geometries': geometry_list}

            if bbox:
                if bbox_geometry_collection:
                    geometry_collection['bbox'] = bbox_geometry_collection
        else:
            geometry_collection = {'type': 'GeometryCollection', 'geometries': []}

    return geometry_collection


def single_geometry_to_multi_geometry(geometry, bbox=True):
    """
    Transform a single geometry (Point, Linestring or Polygon) to multi geometry (MultiPoint, MultiLineString,
    MultiPolygon).

    Equivalent to st_multi() in postgis

    :param geometry: geometry to transform to Multi geometry
    :return: mutli geometry
    """
    original_type = geometry['type']

    geometry_collection = geometry_to_geometry_collection(geometry=geometry, bbox=bbox)
    output_geometry_list = geometry_collection['geometries']

    for geometry_in_collection in output_geometry_list:
        if not 'MULTI' in geometry_in_collection['type'].upper():
            geometry_in_collection['type'] = 'Multi' + geometry_in_collection['type']
            geometry_in_collection['coordinates'] = [geometry_in_collection['coordinates']]

    if original_type.upper() != 'GEOMETRYCOLLECTION':
        output_geometry = output_geometry_list[0]
    else:
        output_geometry = geometry_collection

    return output_geometry


def multi_geometry_to_single_geometry(geometry, bbox=True):
    """
    Iterator in given geometry and send single geometry (Point, LineString, Polygon) if geometry is a multigeometry.
    Works with GeometryCollection
    """

    if geometry['type'].upper() == 'GEOMETRYCOLLECTION':
        for inside_geometry in geometry['geometries']:
            for single_geom in multi_geometry_to_single_geometry(inside_geometry, bbox=bbox):
                if bbox is True:
                    single_geom['bbox'] = coordinates_to_bbox(single_geom['coordinates'])
                yield single_geom

    elif geometry['type'].upper() in {'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON'}:
        if geometry['type'].upper() == 'MULTIPOINT':
            single_geometry_type = 'Point'
        elif geometry['type'].upper() == 'MULTILINESTRING':
            single_geometry_type = 'LineString'
        else:
            single_geometry_type = 'Polygon'

        multi_coordinates = geometry['coordinates']
        for coordinates in multi_coordinates:
            output_geometry = {'type': single_geometry_type, 'coordinates': coordinates}
            if bbox is True:
                output_geometry['bbox'] = coordinates_to_bbox(coordinates)
            yield output_geometry

    else:
        output_geometry = copy.deepcopy(geometry)
        if bbox is True:
            if 'bbox' not in geometry:
                output_geometry['bbox'] = coordinates_to_bbox(output_geometry['coordinates'])
        yield output_geometry


def geometry_to_multi_geometry(geometry, bbox=True):
    """
    Convert a single geometry to multi geometry.

    :param geometry: input geometry
    :param bbox: boolean that indicate if we want or not the bbox information in geometry
    :return: geometry transform to multi geometry
    """

    if 'GEOMETRYCOLLECTION' in geometry['type'].upper():
        output_geometry = {"type": "GeometryCollection"}
        geometries_list = [None] * len(geometry["geometries"])
        compute_bbox = False
        if bbox is True:
            if "bbox" in geometry:
                compute_bbox = False
                collection_bbox = geometry["bbox"]
            else:
                compute_bbox = True

        for i_geom, geometry_in_collection in enumerate(geometry["geometries"]):
            geometry_in_multi = geometry_to_multi_geometry(geometry_in_collection, bbox=bbox)
            geometries_list[i_geom] = geometry_in_multi
            if compute_bbox is True:
                if i_geom == 0:
                    collection_bbox = geometry_in_multi["bbox"]
                else:
                    collection_bbox = bbox_union(collection_bbox, geometry_in_multi["bbox"])

        output_geometry["geometries"] = geometries_list

        if bbox is True:
            output_geometry["bbox"] = collection_bbox
    else:
        if 'MULTI' in geometry['type'].upper():
            output_geometry = copy.deepcopy(geometry)
        else:
            output_geometry = {"type": "Multi" + geometry["type"], "coordinates": [geometry["coordinates"]]}

        if bbox is True:
            if 'bbox' in geometry:
                output_geometry['bbox'] = geometry['bbox']
            else:
                output_geometry['bbox'] = coordinates_to_bbox(geometry['coordinates'])

    return output_geometry


def ogr_geometry_to_geometry(ogr_geometry, bbox=True):
    """
    Convert GDAL/OGR geometry to geoformat geometry

    :param ogr_geometry: ogr geometry class
    :param bbox: boolean that indicate if we want or not the bbox information in geometry
    :return: geoformat geometry
    """

    def coordinates_loop(ogr_geometry, bbox_launch):
        # if geometry is empty
        if ogr_geometry.IsEmpty() is True:
            return [], None
        else:
            bbox = ()
            # if geometry collection
            if ogr_geometry.GetGeometryType() == 7:
                geom_collection_list = []
                for i, under_geom in enumerate(ogr_geometry):
                    geom_geojson = ogr_geometry_to_geometry(
                        ogr_geometry=under_geom,
                        bbox=bbox_launch
                    )
                    geom_collection_list.append(geom_geojson)
                    if bbox_launch and 'bbox' in geom_geojson:
                        if bbox == ():
                            bbox = geom_geojson.get('bbox')
                        else:
                            bbox = bbox_union(bbox, geom_geojson['bbox'])

                return geom_collection_list, tuple(bbox)

            # if point
            elif ogr_geometry.GetGeometryType() == 1:
                coordinates = [ogr_geometry.GetX(), ogr_geometry.GetY()]
                bbox = (ogr_geometry.GetX(), ogr_geometry.GetY(), ogr_geometry.GetX(), ogr_geometry.GetY())

                return coordinates, bbox

            # for linestring, polygon, multipoint, multilinestring, multipolygon
            else:
                # iterate over geometries
                if ogr_geometry.GetGeometryCount() > 0:
                    coordinates_list = [0] * ogr_geometry.GetGeometryCount()
                    for j, under_geom in enumerate(ogr_geometry):
                        # linearring compose polygon if j > 0 then j is a hole.
                        # Hole is inside polygon so we do not need to loop on this coordinate
                        if under_geom.GetGeometryName() == 'LINEARRING' and j > 0:
                            bbox_launch = False
                        else:
                            bbox_launch = True

                        coordinates_list[j], under_bbox = coordinates_loop(under_geom, bbox_launch)
                        if bbox_launch:
                            # bbox
                            if bbox == () and under_bbox:
                                bbox = under_bbox
                            else:
                                bbox = bbox_union(bbox, under_bbox)

                    return coordinates_list, tuple(bbox)

                # iterate over points
                if ogr_geometry.GetPointCount() > 0:
                    coordinates_list = [0] * ogr_geometry.GetPointCount()
                    for i in range(ogr_geometry.GetPointCount()):
                        # coordinates
                        point = ogr_geometry.GetPoint(i)
                        coordinates_list[i] = [point[0], point[1]]
                        # bbox
                        if bbox_launch:
                            if i == 0:
                                bbox = [point[0], point[1], point[0], point[1]]
                            else:
                                if point[0] < bbox[0]:
                                    bbox[0] = point[0]
                                if point[0] > bbox[2]:
                                    bbox[2] = point[0]
                                if point[1] < bbox[1]:
                                    bbox[1] = point[1]
                                if point[1] > bbox[3]:
                                    bbox[3] = point[1]

                    return coordinates_list, tuple(bbox)

    if import_ogr_success:
        geometry = {}
        ogr_geom_type = ogr_geometry.GetGeometryType()
        geometry['type'] = GEOMETRY_CODE_TO_GEOMETRY_TYPE[ogr_geom_type]

        geometry_coordinates, geometry_bbox = coordinates_loop(
            ogr_geometry=ogr_geometry,
            bbox_launch=bbox
        )

        # adding bbox
        if geometry_coordinates and bbox is True:
            geometry['bbox'] = geometry_bbox

        # adding coordinates for geometries
        # if GeometryCollection
        if ogr_geom_type != 7:
            geometry['coordinates'] = geometry_coordinates
        # for others geometries
        else:
            geometry['geometries'] = geometry_coordinates

        return geometry
    else:
        raise Exception(import_ogr_error)


def geometry_to_ogr_geometry(geometry):
    """
    Convert geometry to GDAL/OGR geometry

    :param geometry: input geometry
    :return: ogr geometry object
    """

    def coordinates_loop(coordinates, ogr_geom):
        """
        2D ONLY -- if 3D change AddPoint_2D by AddPoint and add 3D type in GetGeometryType test.
        :param coordinates:
        :param ogr_geom:
        :return:
        """

        if coordinates:
            # if geometry collection
            if ogr_geom.GetGeometryType() == 7:
                for geojson_geom in coordinates:
                    new_ogr_geom = geometry_to_ogr_geometry(geojson_geom)
                    ogr_geom.AddGeometry(new_ogr_geom)

                return ogr_geom

            # if point
            elif ogr_geom.GetGeometryType() == 1:
                ogr_geom.AddPoint_2D(coordinates[0], coordinates[1])
                return ogr_geom

            # for linestring, polygon, multipoint, multilinestring, multipolygon
            else:
                if ogr_geom.GetGeometryType() == 4:
                    under_ogr_geom = ogr.Geometry(ogr.wkbPoint)
                elif ogr_geom.GetGeometryType() == 6:
                    under_ogr_geom = ogr.Geometry(ogr.wkbPolygon)
                elif ogr_geom.GetGeometryType() == 3:
                    under_ogr_geom = ogr.Geometry(ogr.wkbLinearRing)
                elif ogr_geom.GetGeometryType() == 5:
                    under_ogr_geom = ogr.Geometry(ogr.wkbLineString)

                for i, coordinates_list in enumerate(coordinates):
                    if ogr_geom.GetGeometryType() == 2:
                        if i == 0:
                            if ogr_geom.GetGeometryName() == 'LINESTRING':
                                ogr_geom = ogr.Geometry(ogr.wkbLineString)
                            else:
                                ogr_geom = ogr.Geometry(ogr.wkbLinearRing)
                        ogr_geom.AddPoint_2D(coordinates_list[0], coordinates_list[1])

                    else:
                        if i == 0 and ogr_geom.GetGeometryType() == 3:
                            ogr_geom = ogr.Geometry(ogr.wkbPolygon)
                        new_geom = coordinates_loop(coordinates_list, under_ogr_geom)
                        ogr_geom.AddGeometry(new_geom)

        return ogr_geom

    if import_ogr_success:
        geo_type = geometry['type']
        if geo_type.upper() == 'POINT':
            ogr_geom = ogr.Geometry(ogr.wkbPoint)
        elif geo_type.upper() == 'LINESTRING':
            ogr_geom = ogr.Geometry(ogr.wkbLineString)
        elif geo_type.upper() == 'POLYGON':
            ogr_geom = ogr.Geometry(ogr.wkbPolygon)
        elif geo_type.upper() == 'MULTIPOINT':
            ogr_geom = ogr.Geometry(ogr.wkbMultiPoint)
        elif geo_type.upper() == 'MULTILINESTRING':
            ogr_geom = ogr.Geometry(ogr.wkbMultiLineString)
        elif geo_type.upper() == 'MULTIPOLYGON':
            ogr_geom = ogr.Geometry(ogr.wkbMultiPolygon)
        elif geo_type.upper() == 'GEOMETRYCOLLECTION':
            ogr_geom = ogr.Geometry(ogr.wkbGeometryCollection)
        elif geo_type.upper() == 'NO GEOMETRY':
            ogr_geom = ogr.Geometry(ogr.wkbNone)
        elif geo_type.upper() == 'GEOMETRY':
            ogr_geom = ogr.Geometry(ogr.wkbUnknown)
        else:
            ogr_geom = ogr.Geometry(ogr.wkbUnknown)

        if geo_type.upper() != 'NO GEOMETRY':
            if geo_type.upper() != 'GEOMETRYCOLLECTION':
                ogr_geom = coordinates_loop(geometry['coordinates'], ogr_geom)
            else:
                ogr_geom = coordinates_loop(geometry['geometries'], ogr_geom)

        return ogr_geom
    else:
        raise Exception(import_ogr_error)


def geometry_to_wkb(geometry, endian_big=True):
    """
    Transform geoformat geometry (or geojson like geometry) to wkb geometry.
    Optionally you can choose the output endian.

    :param geometry: geoformat geometry (or geojson like geometry)
    :param endian_big: True if output big endian / False if output little endian.
    :return: output bytes geometry in wkb format
    """

    # START geometry_to_wkb
    if endian_big is True:
        endian_b = b'\x00'
    else:
        endian_b = b'\x01'

    geojson_type = geometry['type'].upper()
    multi_geometry = False
    if 'MULTI' in geojson_type:
        multi_geometry = True

    geometry_collection = False
    if geojson_type == 'GEOMETRYCOLLECTION':
        geometry_collection = True

    bytes_geo_type = bytearray(geometry_type_to_wkb_geometry_type[geojson_type])
    if endian_big is False:
        bytes_geo_type.reverse()

    if geometry_collection:
        if geometry['geometries']:
            wkb_coordinates = int_to_4_bytes_integer(integer_value=len(geometry['geometries']),
                                                     integer_endian_big=endian_big)
            for geometry_from_collection in geometry['geometries']:
                wkb_coordinates += geometry_to_wkb(geometry=geometry_from_collection, endian_big=endian_big)
        else:
            wkb_coordinates = b'\x00\x00\x00\x00'
    elif multi_geometry:
        if geometry['coordinates']:
            wkb_coordinates = int_to_4_bytes_integer(integer_value=len(geometry['coordinates']),
                                                     integer_endian_big=endian_big)
            for single_geom in multi_geometry_to_single_geometry(geometry, bbox=False):
                wkb_coordinates += geometry_to_wkb(geometry=single_geom, endian_big=endian_big)
        else:
            wkb_coordinates = b'\x00\x00\x00\x00'
    else:
        if geometry['coordinates']:
            wkb_coordinates = coordinates_list_to_bytes(geometry['coordinates'], coordinates_big_endian=endian_big)
        else:
            if geojson_type == 'POINT':
                if endian_big:
                    wkb_coordinates = b'\x7f\xf8\x00\x00\x00\x00\x00\x00\x7f\xf8\x00\x00\x00\x00\x00\x00'
                else:
                    wkb_coordinates = b'\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'
            else:
                wkb_coordinates = b'\x00\x00\x00\x00'

    wkb_bytearray = endian_b + bytes_geo_type + wkb_coordinates

    return wkb_bytearray


def wkb_to_geometry(wkb_geometry, bbox=True):
    """
    Transform wkb bytes geometry to geoformat (geojson like) geometry

    :param wkb_geometry: input wkb bytes
    :param bbox: boolean that indicate if we want or not the bbox information in geometry
    :return: geoformat geometry (geojson like)
    """

    def define_geometry_lenght_in_bytesarray(geometry_b, geometry_start_idx):
        """
        Return the geometry length (in number of bytes).

        :param geometry_b: geometry in wkb.
        :param geometry_start_idx: start index of geometrie in geometry_b.
        :return: length in integer.
        """
        # determine endian
        endian_b = geometry_b[geometry_start_idx]
        part_big_endian = True
        if endian_b == 1:
            part_big_endian = False
        geometry_start_idx += 1
        # determine geo type
        geometry_end_idx = geometry_start_idx + 4
        _geo_type_b = geometry_b[geometry_start_idx:geometry_end_idx]
        if part_big_endian is False:
            _geo_type_b = bytearray(_geo_type_b)
            _geo_type_b.reverse()
            _geo_type_b = bytes(_geo_type_b)
        _geo_type = big_endian_wkb_geometry_type_to_geometry_type[_geo_type_b]
        # deduce double_dimension
        _dimension = geometry_type_to_dimension[_geo_type]
        geometry_start_idx = geometry_end_idx
        geometry_end_idx = geometry_end_idx + 4
        if 'Multi' in _geo_type:
            _geometry_idx_length = 9
            nb_part_b = geometry_b[geometry_start_idx:geometry_end_idx]
            nb_part = integer_4_bytes_to_int(integer_4_bytes=nb_part_b, integer_endian_big=part_big_endian)
            geometry_start_idx = geometry_end_idx
            for i_part in range(nb_part):
                length_part = define_geometry_lenght_in_bytesarray(geometry_b=geometry_b,
                                                                   geometry_start_idx=geometry_start_idx)
                _geometry_idx_length += length_part
                geometry_start_idx += length_part
        elif _geo_type == 'Point':
            _geometry_idx_length = 5 + _dimension * 8
        else:
            # determine nb coordinates or rings
            _nb_coordinates_or_rings_b = geometry_b[geometry_start_idx:geometry_end_idx]
            _nb_coordinates_or_rings = integer_4_bytes_to_int(integer_4_bytes=_nb_coordinates_or_rings_b,
                                                              integer_endian_big=part_big_endian)
            if 'LineString' in _geo_type:
                # deduce length of linestring part
                _geometry_idx_length = 9 + _dimension * 8 * _nb_coordinates_or_rings
            elif 'Polygon' in _geo_type:
                _geometry_idx_length = 9  # endian + _geo_type + nb_ring
                geometry_start_idx = geometry_end_idx
                # loop on each ring
                for ring in range(_nb_coordinates_or_rings):
                    # deduce nb coordinates by ring
                    geometry_end_idx = geometry_start_idx + 4
                    _nb_coordinates_b = geometry_b[geometry_start_idx:geometry_end_idx]
                    _nb_coordinates = integer_4_bytes_to_int(integer_4_bytes=_nb_coordinates_b,
                                                             integer_endian_big=part_big_endian)
                    # deduce ring length
                    ring_length = 4 + _dimension * 8 * _nb_coordinates  # nb coordinates + length of coordinates
                    _geometry_idx_length += ring_length
                    geometry_start_idx = geometry_start_idx + ring_length
            else:
                raise Exception('geo type not valid')

        return _geometry_idx_length

    def get_coordinates_list_from_wkb_geometry(wkb_coordinates, nb_coord, wkb_dimension, wkb_endian_big=True):
        """
        Determine coordinates list from wkb coordinates. To do that we need the wkb coordinates, the number of
        coordinates and their number of dimensions.
        Optionally you can choose the output endian.

        :param wkb_coordinates: coordinates in wkb
        :param nb_coord: number of coordinates
        :param wkb_dimension: number of dimensions in wkb coordinates
        :param wkb_endian_big: True if output big endian / False if output little endian.
        :return: coordinates list
        """
        _coordinates_list = [None] * nb_coord
        split_idx_list = range(0, nb_coord * wkb_dimension * 8, wkb_dimension * 8)
        for i_coord, _start_idx in enumerate(split_idx_list):
            _end_idx = _start_idx + 8 * wkb_dimension
            part_coordinates_b = wkb_coordinates[_start_idx:_end_idx]
            float_coordinates_list = list(double_8_bytes_to_float(double_8_bytes=part_coordinates_b,
                                                                  double_big_endian=wkb_endian_big,
                                                                  double_dimension=2))
            _coordinates_list[i_coord] = float_coordinates_list

        return _coordinates_list

    # START wkb_to_geometry
    # get endianess of geometry
    geometry_endian_b = wkb_geometry[0]
    if geometry_endian_b == 0:
        endian_big = True
    elif geometry_endian_b == 1:
        endian_big = False
    else:
        raise ValueError('wkb format must begin by "\x00" for BIG or "\x01" for LITTLE endian')
    # get geotype of geometry
    geo_type_b = wkb_geometry[1:5]
    if endian_big is False:
        geo_type_b = bytearray(geo_type_b)
        geo_type_b.reverse()
        geo_type_b = bytes(geo_type_b)
    geo_type = big_endian_wkb_geometry_type_to_geometry_type[geo_type_b]

    # init output geometry
    return_geometry = {'type': geo_type}
    # init idx
    start_idx = 5
    end_idx = start_idx + 4

    if geo_type == 'GeometryCollection':
        # get number of geometries
        nb_geometries_b = wkb_geometry[start_idx:end_idx]
        nb_geometries = integer_4_bytes_to_int(integer_4_bytes=nb_geometries_b, integer_endian_big=endian_big)
        start_idx = end_idx
        geometries_list = [None] * nb_geometries
        if bbox is True:
            geometry_collection_bbox = ()
        for idx_geometry in range(nb_geometries):
            # get length of geometry in collection (in bytes)
            geometry_in_collection_length = define_geometry_lenght_in_bytesarray(geometry_b=wkb_geometry,
                                                                                 geometry_start_idx=start_idx)
            end_idx = start_idx + geometry_in_collection_length
            # create geometry in collection
            geometry_in_collection_b = wkb_geometry[start_idx:end_idx]
            geometry_in_collection = wkb_to_geometry(geometry_in_collection_b, bbox=bbox)
            # add geometry in geometries_list
            geometries_list[idx_geometry] = geometry_in_collection
            # reset start idx
            start_idx = end_idx
            # add bbox if option is True
            if bbox is True:
                if 'bbox' in geometry_in_collection:
                    geometry_bbox = geometry_in_collection['bbox']
                    if not geometry_collection_bbox:
                        geometry_collection_bbox = geometry_bbox
                    else:
                        geometry_collection_bbox = bbox_union(geometry_bbox, geometry_collection_bbox)

        # add geometries to list
        return_geometry['geometries'] = geometries_list
        # if bbox is True
        if bbox is True and geometry_collection_bbox:
            return_geometry['bbox'] = geometry_collection_bbox

    else:
        dimension = geometry_type_to_dimension[geo_type]
        if 'Multi' in geo_type:
            # idx for nb geometries (4 bytes)
            end_idx = start_idx + 4
            nb_geometries_b = wkb_geometry[start_idx:end_idx]
            nb_geometries = integer_4_bytes_to_int(integer_4_bytes=nb_geometries_b, integer_endian_big=endian_big)
            start_idx = end_idx
            coordinates_list = [None] * nb_geometries
            for i_geometry in range(nb_geometries):
                # get length of geometry
                geometry_idx_length = define_geometry_lenght_in_bytesarray(geometry_b=wkb_geometry,
                                                                           geometry_start_idx=start_idx)
                end_idx = start_idx + geometry_idx_length
                slice_geom_b = wkb_geometry[start_idx:end_idx]
                slice_geom = wkb_to_geometry(slice_geom_b, bbox=False)
                coordinates_list[i_geometry] = slice_geom['coordinates']
                # reset start_idx for next geometry
                start_idx = end_idx
        elif geo_type == 'Point':
            x_y_b = wkb_geometry[start_idx:]
            # check if empty geometry
            if (endian_big and x_y_b == b'\x7f\xf8\x00\x00\x00\x00\x00\x00\x7f\xf8\x00\x00\x00\x00\x00\x00') or (
                    not endian_big and x_y_b == b'\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'):
                coordinates_list = []
            # if not empty geometry get coordinates
            else:
                coordinates = double_8_bytes_to_float(double_8_bytes=x_y_b,
                                                      double_big_endian=endian_big,
                                                      double_dimension=dimension)
                coordinates_list = list(coordinates)
        else:
            # get number of coordinates
            nb_coordinates_or_rings_b = wkb_geometry[start_idx:end_idx]
            nb_coordinates_or_rings = integer_4_bytes_to_int(integer_4_bytes=nb_coordinates_or_rings_b,
                                                             integer_endian_big=endian_big)
            if geo_type == 'LineString':
                len_bytes = nb_coordinates_or_rings * 8 * dimension
                start_idx = end_idx
                end_idx = start_idx + len_bytes
                coordinates_in_wkb = wkb_geometry[start_idx:end_idx]
                # get coordinates
                coordinates_list = get_coordinates_list_from_wkb_geometry(nb_coord=nb_coordinates_or_rings,
                                                                          wkb_coordinates=coordinates_in_wkb,
                                                                          wkb_dimension=dimension,
                                                                          wkb_endian_big=endian_big)
            elif geo_type == 'Polygon':
                # get coordinates in each rings
                ring_list = [None] * nb_coordinates_or_rings
                for i_ring in range(nb_coordinates_or_rings):
                    start_idx = end_idx
                    end_idx = start_idx + 4
                    nb_coordinates_b = wkb_geometry[start_idx:end_idx]
                    # get number of coordinates
                    nb_coordinates = integer_4_bytes_to_int(integer_4_bytes=nb_coordinates_b,
                                                            integer_endian_big=endian_big)
                    len_bytes = nb_coordinates * 8 * dimension
                    start_idx = end_idx
                    end_idx = start_idx + len_bytes
                    coordinates_in_wkb = wkb_geometry[start_idx:end_idx]
                    # get coordinates
                    coordinates_list = get_coordinates_list_from_wkb_geometry(nb_coord=nb_coordinates,
                                                                              wkb_coordinates=coordinates_in_wkb,
                                                                              wkb_dimension=dimension,
                                                                              wkb_endian_big=endian_big)
                    # write coordinates in rings list
                    ring_list[i_ring] = coordinates_list

                coordinates_list = ring_list
            else:
                raise Exception('error on geometry type')

        # add coordinates to geom
        return_geometry['coordinates'] = coordinates_list

        # add bbox if true and not empty geometry
        if bbox is True and coordinates_list:
            return_geometry['bbox'] = coordinates_to_bbox(coordinates_list)

    return return_geometry


def geometry_to_wkt(geometry):
    """
    Convert geoformat geometry to WKT geometry.

    :param geometry: input geometry
    :return: wkt geometry
    """

    def coordinates_list_to_wkt_coordinates(coordinates_list_or_tuple, coordinates_dimension=2):
        """
        Loop over coordinates and return a wkt string of this coordinates

        :param coordinates_list_or_tuple: original list of coordinates
        :param coordinates_dimension: number of dimension for each coordinate vertex
        :return: wkt format coordinates
        """

        if coordinates_list_or_tuple:
            _coordinates_pattern = ' '.join(['{}'] * coordinates_dimension)

            if isinstance(coordinates_list_or_tuple[0], (float, int)):
                _coordinates_txt = _coordinates_pattern.format(*coordinates_list_or_tuple)
            else:  # then it's iterable data
                _coordinates_txt = ''
                for _coordinates in coordinates_list_or_tuple:
                    _coordinates_txt += coordinates_list_to_wkt_coordinates(coordinates_list_or_tuple=_coordinates,
                                                                            coordinates_dimension=coordinates_dimension) + ','
                _coordinates_txt = '(' + _coordinates_txt[:-1] + ')'
        else:
            _coordinates_txt = "EMPTY"

        return _coordinates_txt

    # START geometry_to_wkt
    geo_type_upper = geometry['type'].upper()

    if geo_type_upper == 'GEOMETRYCOLLECTION':
        if geometry['geometries']:
            coordinates_txt = ''
            for _geometry in geometry['geometries']:
                coordinates_txt += geometry_to_wkt(geometry=_geometry) + ','
            coordinates_txt = '(' + coordinates_txt[:-1] + ')'
        else:
            coordinates_txt = 'EMPTY'
    else:
        # deduce coordinates_dimension
        dimension = geometry_type_to_dimension[geometry['type']]
        coordinates_txt = coordinates_list_to_wkt_coordinates(coordinates_list_or_tuple=geometry['coordinates'],
                                                              coordinates_dimension=dimension)
        if geo_type_upper == 'POINT' and coordinates_txt != 'EMPTY':
            coordinates_txt = '(' + coordinates_txt + ')'

    return geo_type_upper + ' ' + coordinates_txt


def wkt_to_geometry(wkt_geometry, bbox=True):
    """
    Make translation between wkt geometry and geoformat geometry.

    :param wkt_geometry: WKT geometry that we want to convert to geoformat geometry
    :param bbox: boolean that indicate if we want or not the bbox information in geometry
    :return: geoformat geometry
    """

    def get_wkt_geometries_in_collection(wkt_geometries):
        """
        return a list with wkt geometrie from geometrycollection

        :param wkt_geometries:
        :return: list with wkt geometries in it
        """
        # make a list of allowed geometry : ordered count here (when we will use find())
        geometry_type_allowed_in_collection_ordered = ["POINT", "LINESTRING", "POLYGON", "MULTIPOINT",
                                                       "MULTILINESTRING", "MULTIPOLYGON"]
        # create reversed geometry type
        reversed_geotype_list = [geotype[::-1] for geotype in geometry_type_allowed_in_collection_ordered]

        # delete starting and finishing parenthesis
        geometry_in_collection = wkt_geometries[1:-1]
        # reverse coordinates string
        coordinates_wkt_reversed = geometry_in_collection[::-1]

        geometry_in_collection_list = []
        # loop over coordinates_wkt_reversed as long their are data
        while len(coordinates_wkt_reversed) > 0:
            min_find_idx = len(coordinates_wkt_reversed)
            # loop on each reversed geotype in reversed coordinates_wkt_reversed
            for i_geotype, reversed_geotype in enumerate(reversed_geotype_list):
                # determine geotype position in coordinates_wkt_reversed
                find_idx = coordinates_wkt_reversed.find(reversed_geotype)
                # if index is superior than -1 (no match) and inferior to min_find_idx
                if -1 < find_idx <= min_find_idx:
                    min_find_idx = find_idx
                    min_geotype_reversed = reversed_geotype

            # resize index for entire geometry
            geom_idx = min_find_idx + len(min_geotype_reversed)
            # extract geometry
            reversed_geom = coordinates_wkt_reversed[:geom_idx]
            # reverse geom
            geom = reversed_geom[::-1]
            # store geom in geometry_in_collection_list
            geometry_in_collection_list.append(geom)

            # resize coordinates_wkt_reversed
            coordinates_wkt_reversed = coordinates_wkt_reversed[geom_idx + 1:]

        # reverse list to have original geometries order
        geometry_in_collection_list.reverse()

        return geometry_in_collection_list

    def float_or_int_coordinate_str(coordinate_str):
        """
        Make translation between string coordinates to integer to float coordinates.
        EMPTY geometry doesn't exist in geoformat => this function return None value.

        :param coordinate_str: coordinates in string
        :return: corrdinates in int (if no decimal number) or float (if decimal number)
        """
        if '.' in coordinate_str:
            coordinate = float(coordinate_str)
        else:
            coordinate = int(coordinate_str)

        return coordinate

    if '(' in wkt_geometry:
        geo_type_txt = wkt_geometry.split('(')[0].strip().upper()
        output_geometry = {'type': upper_case_to_geometry_type[geo_type_txt]}
        coordinates_wkt = wkt_geometry.split(wkt_geometry.split('(')[0].lstrip())[1]
        if geo_type_txt == 'GEOMETRYCOLLECTION':
            # retrieve in a list geometries stored in coordinates_wkt
            wkt_geometries_list = get_wkt_geometries_in_collection(coordinates_wkt)
            # convert wkt_geometry to geoformat geometries
            output_geometry["geometries"] = [None] * len(wkt_geometries_list)
            if bbox is True:
                geometry_collection_bbox = ()
            for i_geometry, wkt_geometry in enumerate(wkt_geometries_list):
                geoformat_geometry = wkt_to_geometry(wkt_geometry, bbox=bbox)
                # add bbox parameters for geometry and geometry_collection
                if bbox is True:
                    # if geometry is not
                    if 'bbox' in geoformat_geometry:
                        geometry_bbox = geoformat_geometry['bbox']
                        geoformat_geometry['bbox'] = geometry_bbox
                        if not geometry_collection_bbox:
                            geometry_collection_bbox = geometry_bbox
                        else:
                            geometry_collection_bbox = bbox_union(geometry_bbox, geometry_collection_bbox)
                # add geometry in output_geometry
                output_geometry['geometries'][i_geometry] = geoformat_geometry

            # write bbox for geometries
            if bbox is True:
                if geometry_collection_bbox:
                    output_geometry['bbox'] = geometry_collection_bbox
        else:
            # Now we extract coordinates from coordinates_wkt.
            # all geometrie will have same number of parenthesis in coordinates_wkt
            # like this all coordinates will have same depth when we will split str (coordinates_wkt) to extract coordinates
            first_deep = {'POINT', 'LINESTRING', 'POLYGON', 'MULTIPOINT', 'MULTILINESTRING'}
            second_deep = {'POINT', 'LINESTRING', 'MULTIPOINT'}

            # add parentesis
            if geo_type_txt in first_deep:
                coordinates_wkt = '(' + coordinates_wkt + ')'
                if geo_type_txt in second_deep:
                    coordinates_wkt = '(' + coordinates_wkt + ')'

            # for multi point without extra parenthesis
            multipoint_with_extra_parenthesis = False
            if geo_type_txt == 'MULTIPOINT' and set(coordinates_wkt[-4:]) == set(')'):
                coordinates_wkt = coordinates_wkt[1:-1]
                multipoint_with_extra_parenthesis = True

            # split string  coordinates_wkt and iterates through the depth of the coordinates
            coordinates_wkt = coordinates_wkt.split('(((')[1].split(')))')[0]
            coordinates_part = coordinates_wkt.split('((')
            geometry_coordinates_list = [None] * len(coordinates_part)
            for i_part, part in enumerate(coordinates_part):
                format_part = part.split('))')[0]
                coordinates_ring = format_part.split('(')
                geometry_coordinates_list[i_part] = [None] * len(coordinates_ring)
                for i_ring, ring in enumerate(coordinates_ring):
                    ring_format = ring.split(')')[0].replace(', ', ',')
                    coordinates_list = ring_format.split(',')
                    geometry_coordinates_list[i_part][i_ring] = [None] * len(coordinates_list)
                    for i_coord, coordinates in enumerate(coordinates_list):
                        # extract x y coordinates
                        coordinates_x_y = coordinates.split(',')[0]
                        coordinates_x_y = coordinates_x_y.split(' ')
                        # convert coordinates to int or float
                        x = float_or_int_coordinate_str(coordinates_x_y[0])
                        y = float_or_int_coordinate_str(coordinates_x_y[1])
                        coordinates_result = [x, y]
                        # store coordinates in geometry_coordinates_list
                        if multipoint_with_extra_parenthesis:
                            geometry_coordinates_list[i_part][i_ring] = coordinates_result
                        else:
                            geometry_coordinates_list[i_part][i_ring][i_coord] = coordinates_result
                        # calculate bbox
                        if bbox is True:
                            # init bbox
                            if i_part == 0 and i_ring == 0 and i_coord == 0:
                                geometry_bbox = [x, y, x, y]
                            # udpate bbox
                            else:
                                if x < geometry_bbox[0]:
                                    geometry_bbox[0] = x
                                if y < geometry_bbox[1]:
                                    geometry_bbox[1] = y
                                if x > geometry_bbox[2]:
                                    geometry_bbox[2] = x
                                if y > geometry_bbox[3]:
                                    geometry_bbox[3] = y

            # recreate deepest of coordinates list
            if geo_type_txt in first_deep:
                geometry_coordinates_list = geometry_coordinates_list[0]
                if geo_type_txt in second_deep and multipoint_with_extra_parenthesis is False:
                    geometry_coordinates_list = geometry_coordinates_list[0]
                    if geo_type_txt == 'POINT':
                        geometry_coordinates_list = geometry_coordinates_list[0]
            # save coordinate list in geomet
            output_geometry['coordinates'] = geometry_coordinates_list

            # add bbox
            if bbox is True:
                output_geometry['bbox'] = tuple(geometry_bbox)
    else:
        if 'EMPTY' in wkt_geometry:
            geo_type_txt = wkt_geometry.split('EMPTY')[0].strip().upper()
            if geo_type_txt == 'GEOMETRYCOLLECTION':
                output_geometry = {'type': upper_case_to_geometry_type[geo_type_txt], 'geometries': []}
            else:
                output_geometry = {'type': upper_case_to_geometry_type[geo_type_txt], 'coordinates': []}
        else:
            raise Exception('not WKT linestring')

    return output_geometry


def force_rhr(polygon_geometry):
    """
    Forces the orientation of the vertices in a polygon to follow a Right-Hand-Rule, in which the area that is bounded
    by the polygon is to the right of the boundary. In particular, the exterior ring is orientated in a clockwise
    direction and the interior rings in a counter-clockwise direction.

    Equivalent to Postgis : st_forcerhr

    :param polygon_geometry: polygon or multipolygon geometry
    :return: right hand rule polygon or multipolygon
    """

    # filter on geometry type (ONLY POLYGON and MULTIPOLYGON are allowed)
    if 'POLYGON' in polygon_geometry["type"].upper():
        # create output coordinates list (this list will have the same
        # deepest for polygon and multipolygon : we will correct this after).
        if 'MULTI' in polygon_geometry["type"].upper():
            output_coordinates = [None] * len(polygon_geometry['coordinates'])
        else:
            output_coordinates = [None]
        # loop on each part of polygon
        for i_geom, geometry in enumerate(multi_geometry_to_single_geometry(polygon_geometry, bbox=False)):
            output_ring = [None] * len(geometry['coordinates'])
            # loop on each ring
            for i_ring, ring_coordinates in enumerate(geometry['coordinates']):
                ring_direction = ccw_or_cw_boundary(ring_coordinates)
                # for exterior ring
                if i_ring == 0:
                    # if counter clock wise we reverse ring's coordinates
                    if ring_direction == 'CCW':
                        ring_coordinates.reverse()
                # for interrior ring
                else:
                    # if clock wise we reverse ring's coordinates
                    if ring_direction == 'CW':
                        ring_coordinates.reverse()
                # saving ring
                output_ring[i_ring] = ring_coordinates
            # saving part
            output_coordinates[i_geom] = output_ring

        # if input geometry is polygon we restore the deepest of coordinates list
        if polygon_geometry['type'].upper() == 'POLYGON':
            output_coordinates = output_coordinates[0]

        # store result in output geometry
        output_geometry = {"type": polygon_geometry["type"], "coordinates": output_coordinates}

        # if bbox in geometry
        if "bbox" in polygon_geometry:
            output_geometry["bbox"] = polygon_geometry["bbox"]
    else:
        raise Exception('geometry must be POLYGON or MULTIPOLYGON')

    return output_geometry


def geometry_to_bbox(geometry):
    """
    Return bbox of input geometry
    """

    geometry_collection = geometry_to_geometry_collection(geometry, bbox=False)
    geometry_bbox = None
    if geometry_collection['geometries']:
        for geometry in geometry_collection['geometries']:
            bbox = coordinates_to_bbox(geometry['coordinates'])
            if geometry_bbox:
                geometry_bbox = bbox_union(bbox, geometry_bbox)
            else:
                geometry_bbox = bbox
    else:
        geometry_bbox = ()

    return geometry_bbox


def reproject_geometry(geometry, in_crs, out_crs, precision=None):
    """
    Reproject a geometry with an input coordinate reference system to an output coordinate system

    :param geometry: input geometry
    :param in_crs: input coordinate reference system
    :param out_crs: output coordinate system
    :param precision:
    :return: output geometry
    """

    input_geometry_type = geometry["type"]
    # transform geometry in geometry_collection collection
    geometry_collection = geometry_to_geometry_collection(geometry=geometry, bbox=False)
    # loop on each geometries
    for geometry_in_collection in geometry_collection['geometries']:
        reproj_coordinates = format_coordinates(
            coordinates_list_tuple=geometry_in_collection['coordinates'],
            precision=precision,
            in_crs=in_crs,
            out_crs=out_crs
        )
        geometry_in_collection['coordinates'] = reproj_coordinates
    # if input geometry is not GeometryCollection we return geometry's original type
    if input_geometry_type != 'GeometryCollection':
        output_geometry = geometry_collection['geometries'][0]
    else:
        output_geometry = geometry_collection

    return output_geometry



