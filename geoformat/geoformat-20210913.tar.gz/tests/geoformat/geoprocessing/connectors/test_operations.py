from geoformat.geoprocessing.connectors.operations import (
    coordinates_to_point,
    coordinates_to_segment,
    coordinates_to_bbox,
    segment_to_bbox
)


from tests.data.geometries import (
    POINT,
    MULTIPOINT,
    LINESTRING,
    MULTILINESTRING,
    POLYGON,
    MULTIPOLYGON
)

from tests.data.coordinates import (
    linestring_coordinates,
    multilinestring_coordinates,
    polygon_coordinates,
    multipolygon_coordinates
)

from tests.data.segments import (
    segment_a,
    segment_c,
    segment_d,
    segment_b,
    segment_e,
    segment_f,
    segment_g,
    segment_h,
    segment_i,


)

from test_all import test_function

coordinates_to_point_parameters = {
    0: {
        'coordinates': POINT['coordinates'],
        'return_value': ([-115.81, 37.24], ),
    },
    1: {
        'coordinates': MULTIPOINT['coordinates'],
        'return_value': ([-155.52, 19.61], [-156.22, 20.74], [-157.97, 21.46]),
    },
    2: {
        'coordinates': LINESTRING['coordinates'],
        'return_value': ([8.919, 44.4074], [8.923, 44.4075]),
    },
    3: {
        'coordinates': MULTILINESTRING['coordinates'],
        'return_value': ([3.75, 9.25], [-130.95, 1.52], [23.15, -34.25], [-1.35, -4.65], [3.45, 77.95]),
    },
    4: {
        'coordinates': POLYGON['coordinates'],
        'return_value': ([2.38, 57.322], [23.194, -20.28], [-120.43, 19.15], [2.38, 57.322], [-5.21, 23.51], [15.21, -10.81], [-20.51, 1.51], [-5.21, 23.51])
    },
    5: {
        'coordinates': MULTIPOLYGON['coordinates'],
        'return_value': ([3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28], [23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]),
    },
}

coordinates_to_segment_parameters = {
    0: {
        'coordinates': linestring_coordinates,
        'return_value': ([[8.919, 44.4074], [8.923, 44.4075]],)
    },
    1: {
        'coordinates': multilinestring_coordinates,
        'return_value': ([[3.75, 9.25], [-130.95, 1.52]], [[23.15, -34.25], [-1.35, -4.65]], [[-1.35, -4.65], [3.45, 77.95]])
    },
    2: {
        'coordinates': polygon_coordinates,
        'return_value': ([[2.38, 57.322], [23.194, -20.28]], [[23.194, -20.28], [-120.43, 19.15]], [[-120.43, 19.15], [2.38, 57.322]], [[-5.21, 23.51], [15.21, -10.81]], [[15.21, -10.81], [-20.51, 1.51]], [[-20.51, 1.51], [-5.21, 23.51]])
    },
    3: {
        'coordinates': multipolygon_coordinates,
        'return_value': ([[3.78, 9.28], [-130.91, 1.52]], [[-130.91, 1.52], [35.12, 72.234]], [[35.12, 72.234], [3.78, 9.28]], [[23.18, -34.29], [-1.31, -4.61]], [[-1.31, -4.61], [3.41, 77.91]], [[3.41, 77.91], [23.18, -34.29]])
    },
}

coordinates_to_bbox_parameters = {
    0: {
        'coordinates': POINT['coordinates'],
        'return_value': (-115.81, 37.24, -115.81, 37.24),
    },
    1: {
        'coordinates': MULTIPOINT['coordinates'],
        'return_value': (-157.97, 19.61, -155.52, 21.46)
    },
    2: {
        'coordinates': LINESTRING['coordinates'],
        'return_value': (8.919, 44.4074, 8.923, 44.4075),
    },
    3: {
        'coordinates': MULTILINESTRING['coordinates'],
        'return_value': (-130.95, -34.25, 23.15, 77.95),
    },
    4: {
        'coordinates': POLYGON['coordinates'],
        'return_value': (-120.43, -20.28, 23.194, 57.322)
    },
    5: {
        'coordinates': MULTIPOLYGON['coordinates'],
        'return_value': (-130.91, -34.29, 35.12, 77.91)
    },
}

segment_to_bbox_parameters = {
    0: {
        'segment': segment_a,
        'return_value': (0, 0, 0, 1),
    },
    1: {
        'segment': segment_b,
        'return_value': (0, 0, 0, 1),
    },
    2: {
        'segment': segment_c,
        'return_value': (0, -1, 0, 0),
    },
    3: {
        'segment': segment_d,
        'return_value': (0, -1, 0, 0),
    },
    4: {
        'segment': segment_e,
        'return_value': (-1, -1, 1, 1),
    },
    5: {
        'segment': segment_f,
        'return_value': (-1, -1, 1, 1),
    },
    6: {
        'segment': segment_g,
        'return_value': (-1, -1, 1, 1),
    },
    7: {
        'segment': segment_h,
        'return_value': (-1, -1, -1, 1),
    },
    8: {
        'segment': segment_i,
        'return_value': (1, -1, 1, 1),
    },
}


def test_all():
    # coordinates_to_point
    print(test_function(coordinates_to_point, coordinates_to_point_parameters))

    # coordinates_to_segment
    print(test_function(coordinates_to_segment, coordinates_to_segment_parameters))

    # coordinates_to_bbox
    print(test_function(coordinates_to_bbox, coordinates_to_bbox_parameters))

    # segment_to_bbox
    print(test_function(segment_to_bbox, segment_to_bbox_parameters))


if __name__ == '__main__':
    test_all()
