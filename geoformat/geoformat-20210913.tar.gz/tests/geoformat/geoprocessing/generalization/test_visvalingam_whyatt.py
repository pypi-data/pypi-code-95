from test_all import test_function
from geoformat.geoprocessing.generalization.visvalingam_whyatt import visvalingam_whyatt

visvalingam_whyatt_parameters = {
    0: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 0.59,
        'return_value': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [7, 1.5], [8, 3.2]]
    },
    1: {
        'coordinate_list': [[1, 3], [2, 2.3], [3, 1], [4, 2.1], [5, 2.2], [6, 2.1], [7, 1.5], [8, 3.2]],
        'tolerance': 1.01,
        'return_value': [[1, 3], [3, 1], [5, 2.2], [7, 1.5], [8, 3.2]]
    },
    2: { # test triangle before
        'coordinate_list': [[1, 3.5], [4, 0.5], [5, 4.5], [1.5, 5]],
        'tolerance': 7.3,
        'return_value': [[1, 3.5], [1.5, 5]]
    },
    3: {# test triangle after
        'coordinate_list': [[1.5, 5], [5, 4.5], [4, 0.5], [1, 3.5]],
        'tolerance': 7.3,
        'return_value': [[1.5, 5], [1, 3.5]]
    },
    4: {
        'coordinate_list': [[1, 3.5], [4, 0.5], [5, 4.5], [1.5, 5], [4, 0]],
        'tolerance': 7.3,
        'return_value': [[1, 3.5], [4, 0]]
    },
    5: {
        'coordinate_list': [[4, 0], [1.5, 5], [5, 4.5], [4, 0.5], [1, 3.5]],
        'tolerance': 7.3,
        'return_value': [[4, 0], [1, 3.5]]
    },
    6: {
        'coordinate_list': [[1, 3.5], [4, 0.5], [5, 4.5], [1.5, 5], [4, 0], [0, 0]],
        'tolerance': 7.3,
        'return_value': [[1, 3.5], [0, 0]]
    },
    7: {
        'coordinate_list': [[1, 3.5], [4, 0.5], [5, 4.5], [1.5, 5], [0.5, 7.5], [0, 0]],
        'tolerance': 7.1,
        'return_value': [[1, 3.5], [4, 0.5], [5, 4.5], [1.5, 5], [0, 0]]
    },
}


def test_all():

    # visvalingam
    print(test_function(visvalingam_whyatt, visvalingam_whyatt_parameters))


if __name__ == '__main__':
    test_all()
