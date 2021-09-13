from geoformat.obj.geometry import (
    len_coordinates,
    len_coordinates_in_geometry
)

from tests.data.coordinates import (
    point_coordinates,
    linestring_coordinates,
    polygon_coordinates,
    multipoint_coordinates,
    multilinestring_coordinates,
    multipolygon_coordinates
)

from tests.data.geometries import (
    POINT,
    LINESTRING,
    POLYGON,
    MULTIPOINT,
    MULTILINESTRING,
    MULTIPOLYGON,
    GEOMETRYCOLLECTION
)

from test_all import test_function

len_coordinates_parameters = {
    0: {
        "coordinates": point_coordinates,
        "return_value": 1
    },
    1: {
        "coordinates": linestring_coordinates,
        "return_value": 2
    },
    2: {
        "coordinates": polygon_coordinates,
        "return_value": 8
    },
    3: {
        "coordinates": multipoint_coordinates,
        "return_value": 3
    },
    4: {
        "coordinates": multilinestring_coordinates,
        "return_value": 5
    },
    5: {
        "coordinates": multipolygon_coordinates,
        "return_value": 8
    }
}

len_coordinates_in_geometry_parameters = {
    0: {
        "geometry": POINT,
        "return_value": 1
    },
    1: {
        "geometry": LINESTRING,
        "return_value": 2
    },
    2: {
        "geometry": POLYGON,
        "return_value": 8
    },
    3: {
        "geometry": MULTIPOINT,
        "return_value": 3
    },
    4: {
        "geometry": MULTILINESTRING,
        "return_value": 5
    },
    5: {
        "geometry": MULTIPOLYGON,
        "return_value": 8
    },
    6: {
        "geometry": GEOMETRYCOLLECTION,
        "return_value": 27
    },

}


def test_all():

    # len_coordinates
    print(test_function(len_coordinates, len_coordinates_parameters))

    # len_coordinates_in_geometry
    print(test_function(len_coordinates_in_geometry, len_coordinates_in_geometry_parameters))


if __name__ == '__main__':
    test_all()