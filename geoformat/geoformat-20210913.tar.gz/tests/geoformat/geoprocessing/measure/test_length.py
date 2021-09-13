from geoformat.geoprocessing.measure.length import (
    segment_length,
)
from tests.data.segments import (
    segment_a,
    segment_b,
    segment_c,
    segment_d,
    segment_e,
    segment_f,
    segment_g,
    segment_h,
    segment_i
)
from test_all import test_function


segment_length_parameters = {
    0: {
        'segment': segment_a,
        'distance_type': 'EUCLIDEAN',
        'return_value': 1.
    },
    1: {
        'segment': segment_b,
        'distance_type': 'EUCLIDEAN',
        'return_value': 1.
    },
    2: {
        'segment': segment_c,
        'distance_type': 'EUCLIDEAN',
        'return_value': 1.
    },
    3: {
        'segment': segment_d,
        'distance_type': 'EUCLIDEAN',
        'return_value': 1.
    },
    4: {
        'segment': segment_e,
        'distance_type': 'EUCLIDEAN',
        'return_value': 2.8284271247461903
    },
    5: {
        'segment': segment_f,
        'distance_type': 'EUCLIDEAN',
        'return_value': 2.8284271247461903
    },
    6: {
        'segment': segment_g,
        'distance_type': 'EUCLIDEAN',
        'return_value': 2.8284271247461903
    },
    7: {
        'segment': segment_h,
        'distance_type': 'EUCLIDEAN',
        'return_value': 2.
    },
    8: {
        'segment': segment_i,
        'distance_type': 'EUCLIDEAN',
        'return_value': 2.
    }
}


def test_all():
    # segment length
    print(test_function(segment_length, segment_length_parameters))


if __name__ == '__main__':
    test_all()
