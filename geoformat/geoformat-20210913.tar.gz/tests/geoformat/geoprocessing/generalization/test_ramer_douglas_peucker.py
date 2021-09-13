from test_all import test_function
from geoformat.geoprocessing.generalization.ramer_douglas_peucker import ramer_douglas_peucker

from tests.data.coordinates import (
    point_coordinates,
    linestring_coordinates,
    polygon_coordinates
)

ramer_douglas_peucker_parameters = {
    0: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 0.1,
        'return_value': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]]
    },
    1: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 0.2,
        'return_value': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [6, 2.1], [7, 1.5], [8, 3.2]],
    },
    2: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 0.3,
        'return_value': [[1, 3], [3, 1], [4, 2.1], [6, 2.1], [7, 1.5], [8, 3.2]]
    },
    3: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 1.5,
        'return_value': [[1, 3], [3, 1], [8, 3.2]]
    },
    4: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 2.5,
        'return_value': [[1, 3], [8, 3.2]]
    },
    5: {
        'coordinate_list': [],
        'tolerance': 2.5,
        'return_value': []
    },
    6: {
        'coordinate_list': point_coordinates,
        'tolerance': 2.5,
        'return_value': point_coordinates
    },
    7: {
        'coordinate_list': linestring_coordinates,
        'tolerance': 2.5,
        'return_value': linestring_coordinates
    },
    8: {
        'coordinate_list': [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]],
        'tolerance': 0,
        'return_value': [[2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322]]
    },
}


def test_all():
    # ramer_douglas_peucker
    print(test_function(ramer_douglas_peucker, ramer_douglas_peucker_parameters))


if __name__ == '__main__':
    test_all()

