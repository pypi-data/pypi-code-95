from geoformat.geoprocessing.measure.area import (
    shoelace_formula,
    triangle_area
)

from test_all import test_function

shoelace_formula_parameters = {
    0: {
        "ring_coordinates": [[-1, 1], [1, 1], [1, -1], [-1, -1]],  # convex boundary
        "absolute_value": True,
        "return_value": 4.
    },
    1: {
        "ring_coordinates": [[-1, -1], [1, -1], [1, 1], [-1, 1]],  # reverse convex boundary
        "absolute_value": True,
        "return_value": 4.
    },
    2: {
        "ring_coordinates": [[-1, -1], [0, 0], [1, -1], [1, 1], [-1, 1]],  # concave boundary
        "absolute_value": True,
        "return_value": 3.
    },
    3: {
        "ring_coordinates": [[-1, 1], [1, 1], [1, -1], [0, 0], [-1, -1]],  # reverse concave boundary
        "absolute_value": True,
        "return_value": 3.
    },
    4: {
        "ring_coordinates": [[-1, 1], [1, 1], [1, -1], [-1, -1]],  # convex boundary
        "absolute_value": False,
        "return_value": 4.
    },
    5: {
        "ring_coordinates": [[-1, -1], [1, -1], [1, 1], [-1, 1]],  # reverse convex boundary
        "absolute_value": False,
        "return_value": -4.
    },
    6: {
        "ring_coordinates": [[-1, -1], [0, 0], [1, -1], [1, 1], [-1, 1]],  # concave boundary
        "absolute_value": False,
        "return_value": -3.
    },
    7: {
        "ring_coordinates": [[-1, 1], [1, 1], [1, -1], [0, 0], [-1, -1]],  # reverse concave boundary
        "absolute_value": False,
        "return_value": 3.
    },
}


triangle_area_parameters = {
    0: {
        "vertex_a": (0, 1),
        "vertex_b": (1, 0),
        "vertex_c": (0, 0),
        "return_value": 0.5000000000000001
    },
    1: {
        "vertex_a": [1, 3.5],
        "vertex_b": [4, 0.5],
        "vertex_c": [5, 4.5],
        "return_value": 7.5
    },
    2: {
        "vertex_a": [4, 0.5],
        "vertex_b": [5, 4.5],
        "vertex_c": [1.5, 5],
        "return_value": 7.250000000000002
    },
}

def test_all():
    # shoelace_formula
    print(test_function(shoelace_formula, shoelace_formula_parameters))

    # triangle_area
    print(test_function(triangle_area, triangle_area_parameters))


if __name__ == '__main__':
    test_all()
