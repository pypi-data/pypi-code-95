from geoformat.conversion.precision_tolerance_conversion import (
    deduce_rounding_value_from_float,
    deduce_precision_from_round
)

from test_all import test_function

deduce_rounding_value_from_float_parameters = {
    0: {
        'float_value': 56.4325,
        'return_value': 4
    },
    1: {
        'float_value': 56.43256436,
        'return_value': 8
    },
    2: {
        'float_value': -56.4325,
        'return_value': 4
    },
    3: {
        'float_value': -56.43256436,
        'return_value': 8
    }
}

deduce_precision_from_round_parameters = {
    0: {
        'rounding_value': 4,
        'return_value': 0.0001,
    },
    1: {
        'rounding_value': 8,
        'return_value': 0.00000001
    },
    2: {
        'rounding_value': 4,
        'return_value': 0.0001,
    },
    3: {
        'rounding_value': 8,
        'return_value': 0.00000001,
    }
}


def test_all():
    # deduce_rounding_value_from_float
    print(test_function(deduce_rounding_value_from_float, deduce_rounding_value_from_float_parameters))

    # deduce_precision_from_round
    print(test_function(deduce_precision_from_round, deduce_precision_from_round_parameters))

if __name__ == '__main__':
    test_all()
