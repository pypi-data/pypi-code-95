from test_all import test_function
from geoformat.geoprocessing.geoparameters.lines import (
    get_slope_between_two_points,
    get_intercept_from_point_and_slope,
    get_slope_from_point_and_intercept,
    line_parameters,
    perpendicular_line_parameters_at_point,
    point_at_distance_with_line_parameters,
    crossing_point_from_lines_parameters
)

get_slope_between_two_points_parameters = {
    0: {
        "point_a": (0, 0),
        "point_b": (2, 2),
        "return_value": 1
    },
    1: {
        "point_a": (0, 0),
        "point_b": (2, -2),
        "return_value": -1
    },
    2: {
        "point_a": (0, 0),
        "point_b": (2, 0),
        "return_value": 0
    },
    3: {
        "point_a": (-3, -3),
        "point_b": (-3, -5),
        "return_value": 'VERTICAL'
    }
}

get_intercept_from_point_and_slope_parameters = {
    0: {
        "point": (2, 2),
        "slope": 1,
        "return_value": 0
    },
    1: {
        "point": (2, 2),
        "slope": -1,
        "return_value": 4
    },
    2: {
        "point": (-2, -2),
        "slope": 1,
        "return_value": 0
    },
    3: {
        "point": (-2, -2),
        "slope": -1,
        "return_value": -4
    },
    4: {
        "point": (3, 2),
        "slope": 3,
        "return_value": -7
    },
    5: {
        "point": (2, 2),
        "slope": 0,
        "return_value": 2
    },
    6: {
        "point": (-2, -2),
        "slope": 'VERTICAL',
        "return_value": -2
    },
}

get_slope_from_point_and_intercept_parameters = {
    0: {
        "point": (2, 2),
        "return_value": 1,
        "intercept": 0
    },
    1: {
        "point": (2, 2),
        "return_value": -1,
        "intercept": 4
    },
    2: {
        "point": (-2, -2),
        "return_value": 1,
        "intercept": 0
    },
    3: {
        "point": (-2, -2),
        "return_value": -1,
        "intercept": -4
    },
    4: {
        "point": (3, 2),
        "return_value": 3,
        "intercept": -7
    },
    5: {
        "point": (2, 2),
        "return_value": 0,
        "intercept": 2
    },
    6: {
        "point": (-2, -2),
        "return_value": 'VERTICAL',
        "intercept": False
    },
}

line_parameters_parameters = {
    0: {
        'segment': ([645285, 6779558], [647006, 6779454]),
        'return_value': {'slope': -0.06042998256827426, 'intercept': 6818552.5613015685}
    },
    1: {
        'segment': ((10, 10), (100, 20)),
        'return_value': {'slope': 0.1111111111111111, 'intercept': 8.88888888888889}
    },
    2: {
        'segment': ((0, 1), (9, 4)),
        'return_value': {'slope': 1/3, 'intercept': 1.}
    },
    3: {
        'segment': ((-5, 0), (5, 0)),
        'return_value': {'slope': 0.0, 'intercept': 0.0}
    },
    4: {
        'segment': ((0, -5), (0, 5)),
        'return_value': {'slope': 'VERTICAL', 'intercept': 0.0}
    }
}


perpendicular_line_parameters_at_point_parameters = {
    0: {
        'line_parameters': {'slope': 1/3, 'intercept': 1.},
        'point': (3, 2),
        'return_value': {'slope': -3.0, 'intercept': 11.0}
    },
    1: {
        'line_parameters': {'slope': 0.0, 'intercept': 0.0},
        'point': (0, 0),
        'return_value': {'slope': 'VERTICAL', 'intercept': 0.}
    },
    2:  {
        'line_parameters':  {'slope': 'VERTICAL', 'intercept': 5},
        'point': (0, 0),
        'return_value': {'slope': 0., 'intercept': 0.}
    }

}


point_at_distance_with_line_parameters_parameters = {
    0: {
        'start_point': (0, 0),
        'line_parameters':  {'slope': 1, 'intercept': 0},
        'distance': 5,
        'offset_distance': None,
        'return_value': (3.5355339059327373, 3.5355339059327373),
    },
    1: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 'VERTICAL', 'intercept': 0.},
        'distance': 5,
        'offset_distance': None,
        'return_value': (0, 5),
    },
    2: {
        'start_point': (0, 0),
        'line_parameters':  {'slope': 0.0, 'intercept': 0.0},
        'distance': 5,
        'offset_distance': None,
        'return_value': (5, 0),
    },
    3: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 1, 'intercept': 0},
        'distance': 5,
        'offset_distance': 2,
        'return_value': (4.949747468305832, 2.121320343559643),
    },
    4: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 'VERTICAL', 'intercept': 0.},
        'distance': 5,
        'offset_distance': 2,
        'return_value': (2, 5),
    },
    5: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 0.0, 'intercept': 0.0},
        'distance': 5,
        'offset_distance': 2,
        'return_value': (5, 2),
    },
    6: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 1, 'intercept': 0},
        'distance': -5,
        'offset_distance': 2,
        'return_value': (-2.1213203435596424, -4.949747468305832),
    },
    7: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 'VERTICAL', 'intercept': 0.},
        'distance': -5,
        'offset_distance': 2,
        'return_value': (2, -5),
    },
    8: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 0.0, 'intercept': 0.0},
        'distance': -5,
        'offset_distance': 2,
        'return_value': (-5, 2),
    },
    9: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 1, 'intercept': 0},
        'distance': -5,
        'offset_distance': -2,
        'return_value': (-4.949747468305832, -2.121320343559643),
    },
    10: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 'VERTICAL', 'intercept': 0.},
        'distance': -5,
        'offset_distance': -2,
        'return_value': (-2, -5),
    },
    11: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 0.0, 'intercept': 0.0},
        'distance': -5,
        'offset_distance': -2,
        'return_value': (-5, -2),
    },
    12: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 0.0, 'intercept': 0.0},
        'distance': 0,
        'offset_distance': 1,
        'return_value': (0, 1),
    },
    13: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 0.0, 'intercept': 0.0},
        'distance': 0,
        'offset_distance': -1,
        'return_value': (0, -1),
    },
    14: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 'VERTICAL', 'intercept': 0.0},
        'distance': 0,
        'offset_distance': 1,
        'return_value': (1, 0),
    },
    15: {
        'start_point': (0, 0),
        'line_parameters': {'slope': 'VERTICAL', 'intercept': 0.0},
        'distance': 0,
        'offset_distance': -1,
        'return_value': (-1, 0),
    }
}

crossing_point_from_lines_parameters_parameters = {
    0: {
        'line_parameter_a': {'slope': 0.0, 'intercept': 0.0},
        'line_parameter_b': {'slope': 'VERTICAL', 'intercept': 0.},
        'return_value': (0, 0),
    },
    1: {
        'line_parameter_a': {'slope': 0.0, 'intercept': -2},
        'line_parameter_b': {'slope': 'VERTICAL', 'intercept': -3.},
        'return_value': (-3, -2),
    },
    2: {
        'line_parameter_a': {'slope': 1, 'intercept': -2},
        'line_parameter_b': {'slope': -1, 'intercept': -3.},
        'return_value': (-0.5, -2.5),
    },
    3: {
        'line_parameter_a': {'slope': 1, 'intercept': -2},
        'line_parameter_b': {'slope': -1, 'intercept': -3.},
        'return_value': (-0.5, -2.5),
    },
    4: {
        'line_parameter_a': {'slope': 1 / 3, 'intercept': 1.},
        'line_parameter_b': {'slope': -3.0, 'intercept': 11.0},
        'return_value': (3, 2),
    },
    5: {
        'line_parameter_a': {'slope': 1 / 3, 'intercept': 1.},
        'line_parameter_b': {'slope': -3.0, 'intercept': 11.0},
        'return_value': (3, 2),
    },
    6: {
        'line_parameter_a': {'slope': 'VERTICAL', 'intercept': 1419169.19},
        'line_parameter_b':  {'slope': 0.0, 'intercept': 4184658.3044332825},
        'return_value': (1419169.19, 4184658.3044332825)
    },
    7: {
        'line_parameter_a': {'slope': 0.0, 'intercept': 4184658.3044332825},
        'line_parameter_b': {'slope': 'VERTICAL', 'intercept': 1419169.19},
        'return_value': (1419169.19, 4184658.3044332825)
    },
}


def test_all():
    # get_slope_between_two_points
    print(test_function(get_slope_between_two_points, get_slope_between_two_points_parameters))

    # get_intercept_from_point_and_slope
    print(test_function(get_intercept_from_point_and_slope, get_intercept_from_point_and_slope_parameters))

    # get_return_value_from_point_and_intercept_parameters
    print(test_function(get_slope_from_point_and_intercept, get_slope_from_point_and_intercept_parameters))

    # line_parameters
    print(test_function(line_parameters, line_parameters_parameters))

    # perpendicular_line_parameters_at_point
    print(test_function(perpendicular_line_parameters_at_point, perpendicular_line_parameters_at_point_parameters))

    # point_at_distance_with_line_parameters
    print(test_function(point_at_distance_with_line_parameters, point_at_distance_with_line_parameters_parameters))

    # crossing_point_from_lines_parameters
    print(test_function(crossing_point_from_lines_parameters, crossing_point_from_lines_parameters_parameters))


if __name__ == '__main__':
    test_all()
