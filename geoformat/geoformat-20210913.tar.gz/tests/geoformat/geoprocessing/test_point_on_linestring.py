from geoformat.geoprocessing.point_on_linestring import (
    point_at_a_distance_on_segment,
    points_on_linestring_distance
)

from tests.data.geometries import (
    LINESTRING_TEST_POINT_ON_LINESTRING,
    LINESTRING_TEST_POINT_ON_LINESTRING_REVERSE
)


from test_all import test_function

point_at_a_distance_on_segment_parameters = {
    0: {
        "segment": ((-10, 0), (10, 0)),
        "step_distance": 5,
        "offset_distance": None,
        "return_value": ((-5, 0), (0, 0), (5, 0), (10, 0))
    },
    1: {
        "segment": ((0, -10), (0, 10)),
        "step_distance": 5,
        "offset_distance": None,
        "return_value": ((0, -5), (0, 0), (0, 5), (0, 10))
    },
    2: {
        "segment": ((10, 0), (-10, 0)),
        "step_distance": 5,
        "offset_distance": None,
        "return_value": ((5, 0), (0, 0), (-5, 0), (-10, 0))
    },
    3: {
        "segment": ((0, 10), (0, -10)),
        "step_distance": 5,
        "offset_distance": None,
        "return_value": ((0, 5), (0, 0), (0, -5), (0, -10))
    },
    4: {
        "segment": ((-10, 0), (10, 0)),
        "step_distance": 5,
        "offset_distance": 1,
        "return_value": ((-5., 1.), (0., 1.), (5., 1.), (10.0, 1.0))
    },
    5: {
        "segment": ((0, -10), (0, 10)),
        "step_distance": 5,
        "offset_distance": -1,
        "return_value": ((-1., -5), (-1., 0), (-1., 5), (-1.0, 10.0))
    },
    6: {
        "segment": ((-10, -10), (10, 10)),
        "step_distance": 5,
        "offset_distance": 0,
        "return_value": ((-6.464466094067262, -6.464466094067262), (-2.928932188134525, -2.928932188134525),
                         (0.6066017177982124, 0.6066017177982124), (4.142135623730949, 4.142135623730949),
                         (7.677669529663687, 7.677669529663687))
    },
    7: {
        "segment": ((10, 10), (-10, -10)),
        "step_distance": 5,
        "offset_distance": 0,
        "return_value": ((6.464466094067262, 6.464466094067262), (2.928932188134525, 2.928932188134525),
                         (-0.6066017177982124, -0.6066017177982124), (-4.142135623730949, -4.142135623730949),
                         (-7.677669529663687, -7.677669529663687))
    },
    8: {
        "segment": ((-10, 10), (10, -10)),
        "step_distance": 5,
        "offset_distance": 0,
        "return_value": ((-6.464466094067262, 6.464466094067262), (-2.928932188134525, 2.928932188134525),
                         (0.6066017177982124, -0.6066017177982124), (4.142135623730949, -4.142135623730949),
                         (7.677669529663687, -7.677669529663687))
    },
    9: {
        "segment": ((10, -10), (-10, 10)),
        "step_distance": 5,
        "offset_distance": 0,
        "return_value": ((6.464466094067262, -6.464466094067262), (2.928932188134525, -2.928932188134525),
                         (-0.6066017177982124, 0.6066017177982124), (-4.142135623730949, 4.142135623730949),
                         (-7.677669529663687, 7.677669529663687))
    },
}

points_on_linestring_distance_parameters = {
    0: {
        "linestring": LINESTRING_TEST_POINT_ON_LINESTRING,
        "step_distance": 5,
        "offset_distance": None,
        "return_value": ({'type': 'Point', 'coordinates': [-10, -10]}, {'type': 'Point', 'coordinates': [-10, -5]}, {'type': 'Point', 'coordinates': [-10, 0]}, {'type': 'Point', 'coordinates': [-10, 5]}, {'type': 'Point', 'coordinates': [-10.0, 10.0]}, {'type': 'Point', 'coordinates': [-5.0, 10.0]}, {'type': 'Point', 'coordinates': [0.0, 10.0]}, {'type': 'Point', 'coordinates': [5.0, 10.0]}, {'type': 'Point', 'coordinates': [10.0, 10.0]})
    },
    1: {
        "linestring": LINESTRING_TEST_POINT_ON_LINESTRING_REVERSE,
        "step_distance": 5,
        "offset_distance": None,
        "return_value": ({'type': 'Point', 'coordinates': [10.0, 10.0]}, {'type': 'Point', 'coordinates': [5.0, 10.0]}, {'type': 'Point', 'coordinates': [0.0, 10.0]}, {'type': 'Point', 'coordinates': [-5.0, 10.0]}, {'type': 'Point', 'coordinates': [-10.0, 10.0]}, {'type': 'Point', 'coordinates': [-10, 5]}, {'type': 'Point', 'coordinates': [-10, 0]}, {'type': 'Point', 'coordinates': [-10, -5]}, {'type': 'Point', 'coordinates': [-10, -10]})
    }
}


def test_all():
    # point_at_a_distance_on_segment
    print(test_function(point_at_a_distance_on_segment, point_at_a_distance_on_segment_parameters))

    # points_on_linestring_distance
    print(test_function(points_on_linestring_distance, points_on_linestring_distance_parameters))


if __name__ == '__main__':
    test_all()
