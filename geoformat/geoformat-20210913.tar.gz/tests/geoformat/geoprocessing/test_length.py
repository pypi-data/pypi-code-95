from geoformat.geoprocessing.length import (
    geometry_length
)
from tests.data.geometries import (
    POINT,
    POINT_EMPTY,
    LINESTRING,
    LINESTRING_EMPTY,
    POLYGON,
    POLYGON_EMPTY,
    MULTIPOINT,
    MULTIPOINT_EMPTY,
    MULTILINESTRING,
    MULTILINESTRING_EMPTY,
    MULTIPOLYGON,
    MULTIPOLYGON_EMPTY,
    GEOMETRYCOLLECTION,
    GEOMETRYCOLLECTION_EMPTY
)
from test_all import test_function

geometry_length_parameters = {
    0: {
        "geometry": POINT,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0,
    },
    1: {
        "geometry": POINT_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0,
    },
    2: {
        "geometry": LINESTRING,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0.004001249804747976
    },
    3: {
        "geometry": LINESTRING_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0
    },
    4: {
        "geometry": POLYGON,
        "distance_type": 'EUCLIDEAN',
        "return_value": 462.40615942416747
    },
    5: {
        "geometry": POLYGON_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0,
    },
    6: {
        "geometry": MULTIPOINT,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0
    },
    7: {
        "geometry": MULTIPOINT_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0
    },
    8: {
        "geometry": MULTILINESTRING,
        "distance_type": 'EUCLIDEAN',
        "return_value": 256.0850483743341
    },
    9: {
        "geometry": MULTILINESTRING_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0
    },
    10: {
        "geometry": MULTIPOLYGON,
        "distance_type": 'EUCLIDEAN',
        "return_value": 620.7613322414908
    },
    11: {
        "geometry": MULTIPOLYGON_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0
    },
    12: {
        "geometry": GEOMETRYCOLLECTION,
        "distance_type": 'EUCLIDEAN',
        "return_value": 1339.256541289797
    },
    13: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "distance_type": 'EUCLIDEAN',
        "return_value": 0
    },
}


def test_all():
    # geometry length
    print(test_function(geometry_length, geometry_length_parameters))


if __name__ == '__main__':
    test_all()
