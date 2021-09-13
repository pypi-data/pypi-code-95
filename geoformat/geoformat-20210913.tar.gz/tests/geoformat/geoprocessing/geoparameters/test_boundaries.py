from geoformat.geoprocessing.geoparameters.boundaries import ccw_or_cw_boundary

from test_all import test_function

ccw_or_cw_boundary_parameters = {
    0: {
        "boundary_coordinates": [[-1, 1], [1, 1], [1, -1], [-1, -1]],  # convex boundary
        "return_value": 'CW'
    },
    1: {
        "boundary_coordinates": [[-1, -1], [1, -1], [1, 1], [-1, 1]],  # reverse convex boundary
        "return_value": 'CCW'
    },
    2: {
        "boundary_coordinates": [[-1, -1], [0, 0], [1, -1], [1, 1], [-1, 1]],  # concave boundary
        "return_value": 'CCW'
    },
    3: {
        "boundary_coordinates": [[-1, 1], [1, 1], [1, -1], [0, 0], [-1, -1]],  # reverse concave boundary
        "return_value": 'CW'
    }
}


def test_all():
    # ccw_or_cw_boundary
    print(test_function(ccw_or_cw_boundary, ccw_or_cw_boundary_parameters))


if __name__ == '__main__':
    test_all()