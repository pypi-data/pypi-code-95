from geoformat.geoprocessing.measure.distance import (
    euclidean_distance,
    manhattan_distance,
    euclidean_distance_point_vs_segment,
    point_vs_segment_distance
)
from test_all import test_function


euclidean_distance_parameters = {
    0: {
        'point_a': (0, 0),
        'point_b': (0, 5),
        'return_value': 5
    },
    1:  {
        'point_a': (-5, -1),
        'point_b': (-5, -4),
        'return_value': 3
    },
    2:  {
        'point_a': (3, 2),
        'point_b': (9, 7),
        'return_value': 7.810249675906654
    },
    3:  {
        'point_a': (-2, -2),
        'point_b': (0, -4),
        'return_value': 2.8284271247461903
    },
    4:  {
        'point_a': [23.194, -20.28],
        'point_b': [2.38, 57.322],
        'return_value': 80.3448380420298
    },
}

manhattan_distance_parameters = {
    0: {
        'point_a': (0, 0),
        'point_b': (0, 5),
        'return_value': 5
    },
    1:  {
        'point_a': (-5, -1),
        'point_b': (-5, -4),
        'return_value': 3
    },
    2:  {
        'point_a': (3, 2),
        'point_b': (9, 7),
        'return_value': 11
    },
    3:  {
        'point_a': (-2, -2),
        'point_b': (0, -4),
        'return_value': 4
    },
}

euclidean_distance_point_vs_segment_parameters = {
    0: {
        'point': (0, 4),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 0
    },
    1: {
        'point': (0, 3),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 1
    },
    2: {
        'point': (0, 3),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 1
    },
    3: {
        'point': (6, 3),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 1.4142135623730951
    },
    4: {
        'point': [23.194, -20.28],
        'segment': [[2.38, 57.322], [2.38, 57.322]],
        'return_value': 80.3448380420298
    }
}

point_vs_segment_distance_parameters = {
    0: {
        'point': (0, 4),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 0
    },
    1: {
        'point': (0, 3),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 1
    },
    2: {
        'point': (6, 1),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 3.1622776601683795
    },
    3: {
        'point': (6, 3),
        'segment': ((-5, 4), (5, 4)),
        'return_value': 1.4142135623730951
    },
    4: {
        'point': (0, 4),
        'segment': ((-5, 4), (5, 4)),
        'distance_function': manhattan_distance,
        'return_value': 0,
    },
    5: {
        'point': (0, 3),
        'segment': ((-5, 4), (5, 4)),
        'distance_function': manhattan_distance,
        'return_value': 1
    },
    6: {
        'point': (6, 1),
        'segment': ((-5, 4), (5, 4)),
        'distance_function': manhattan_distance,
        'return_value': 4
    },
    7: {
        'point': (6, 3),
        'segment': ((-5, 4), (5, 4)),
        'distance_function': manhattan_distance,
        'return_value': 2
    },
    8: {
        'point': [23.194, -20.28],
        'segment': [[2.38, 57.322], [2.38, 57.322]],
        'distance_function': euclidean_distance,
        'return_value': 80.3448380420298
    }
}


def test_all():
    # euclidean_distance
    print(test_function(euclidean_distance, euclidean_distance_parameters))

    # manhattan_distance
    print(test_function(manhattan_distance, manhattan_distance_parameters))

    # euclidean_distance_point_vs_segment
    print(test_function(euclidean_distance_point_vs_segment, euclidean_distance_point_vs_segment_parameters))

    # point_vs_segment_distance
    print(test_function(point_vs_segment_distance, point_vs_segment_distance_parameters))


if __name__ == '__main__':
    test_all()
