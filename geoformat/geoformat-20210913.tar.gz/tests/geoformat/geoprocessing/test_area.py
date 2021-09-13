from geoformat.geoprocessing.area import (
    geometry_area
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

geometry_area_parameters = {
    0: {
        "geometry": POINT,
        "return_value": 0,
    },
    1: {
        "geometry": POINT_EMPTY,
        "return_value": 0,
    },
    2: {
        "geometry": LINESTRING,
        "return_value": 0
    },
    3: {
        "geometry": LINESTRING_EMPTY,
        "return_value": 0
    },
    4: {
        "geometry": POLYGON,
        "return_value": 4675.238814000001
    },
    5: {
        "geometry": POLYGON_EMPTY,
        "return_value": 0,
    },
    6: {
        "geometry": MULTIPOINT,
        "return_value": 0
    },
    7: {
        "geometry": MULTIPOINT_EMPTY,
        "return_value": 0
    },
    8: {
        "geometry": MULTILINESTRING,
        "return_value": 0
    },
    9: {
        "geometry": MULTILINESTRING_EMPTY,
        "return_value": 0
    },
    10: {
        "geometry": MULTIPOLYGON,
        "return_value": 5198.540129999999
    },
    11: {
        "geometry": MULTIPOLYGON_EMPTY,
        "return_value": 0
    },
    12: {
        "geometry": GEOMETRYCOLLECTION,
        "return_value": 9873.778944000002
    },
    13: {
        "geometry": GEOMETRYCOLLECTION_EMPTY,
        "return_value": 0
    },
}


def test_all():
    # geometry_area
    print(test_function(geometry_area, geometry_area_parameters))


if __name__ == '__main__':
    test_all()

