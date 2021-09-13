from test_all import test_function
from tests.data.geometries import (
    POINT,
    POINT_EMPTY,
    LINESTRING,
    LINESTRING_EMPTY,
    POLYGON,
    POLYGON_EMPTY,
    MULTIPOINT,
    MULTILINESTRING,
    MULTIPOLYGON,
    GEOMETRYCOLLECTION,
    GEOMETRYCOLLECTION_EMPTY
)
from geoformat.geoprocessing.merge_geometries import merge_geometries

merge_geometries_parameters = {
    0: {
        "geom_a": POINT,
        "geom_b": POINT_EMPTY,
        "bbox": False,
        "return_value": POINT
    },
    1: {
        "geom_a": LINESTRING,
        "geom_b": LINESTRING_EMPTY,
        "bbox": False,
        "return_value": LINESTRING
    },
    2: {
        "geom_a": POLYGON,
        "geom_b": POLYGON_EMPTY,
        "bbox": False,
        "return_value": POLYGON
    },
    3: {
        "geom_a": POINT,
        "geom_b": MULTIPOINT,
        "bbox": False,
        "return_value": {'type': 'MultiPoint', 'coordinates': [[-115.81, 37.24], [-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]}
    },
    4: {
        "geom_a": LINESTRING,
        "geom_b": MULTILINESTRING,
        "bbox": False,
        "return_value": {'type': 'MultiLineString', 'coordinates': [[[8.919, 44.4074], [8.923, 44.4075]], [[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]}
    },
    5: {
        "geom_a": POLYGON,
        "geom_b": MULTIPOLYGON,
        "bbox": False,
        "return_value": {'type': 'MultiPolygon', 'coordinates': [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]], [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}
    },
    6: {
        "geom_a": POINT,
        "geom_b": POLYGON,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [-115.81, 37.24]}, {'type': 'Polygon', 'coordinates': [[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]]}]}
    },
    7: {
        "geom_a": GEOMETRYCOLLECTION,
        "geom_b": POINT,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'MultiPoint', 'coordinates': [[-115.81, 37.24], [-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]}, {'type': 'MultiLineString', 'coordinates': [[[8.919, 44.4074], [8.923, 44.4075]], [[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]}, {'type': 'MultiPolygon', 'coordinates': [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]], [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}]}
    },
    8: {
        "geom_a": POINT_EMPTY,
        "geom_b": POINT_EMPTY,
        "bbox": False,
        "return_value": POINT_EMPTY
    },
    9: {
        "geom_a": POINT_EMPTY,
        "geom_b": POLYGON_EMPTY,
        "bbox": False,
        "return_value": GEOMETRYCOLLECTION_EMPTY
    },
    10: {
        "geom_a": POINT,
        "geom_b": POINT,
        "bbox": False,
        "return_value": POINT
    },
    11: {
        "geom_a": {'type': "MultiPoint", "coordinates": MULTIPOINT['coordinates'] + [POINT['coordinates']]},
        "geom_b": POINT,
        "bbox": False,
        "return_value": {'type': "MultiPoint", "coordinates": MULTIPOINT['coordinates'] + [POINT['coordinates']]}
    },
    12: {
        "geom_a": POINT,
        "geom_b": {'type': "MultiPoint", "coordinates": MULTIPOINT['coordinates'] + [POINT['coordinates']]},
        "bbox": False,
        "return_value": {'type': "MultiPoint", "coordinates": [POINT['coordinates']] + MULTIPOINT['coordinates']}
    },
    13: {
        "geom_a": MULTIPOINT,
        "geom_b": MULTIPOINT,
        "bbox": False,
        "return_value": MULTIPOINT
    },
    14: {
        "geom_a": GEOMETRYCOLLECTION,
        "geom_b": GEOMETRYCOLLECTION,
        "bbox": False,
        "return_value": {'type': 'GeometryCollection', 'geometries': [{'type': 'MultiPoint', 'coordinates': [[-115.81, 37.24], [-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]]}, {'type': 'MultiLineString', 'coordinates': [[[8.919, 44.4074], [8.923, 44.4075]], [[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]]]}, {'type': 'MultiPolygon', 'coordinates': [[[[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51]]], [[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]}]}
    }
}


def test_all():
    # merge_geometries
    print(test_function(merge_geometries, merge_geometries_parameters))


if __name__ == '__main__':
    test_all()
