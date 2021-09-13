from test_all import test_function

from geoformat.conf.format_data import (
    value_to_iterable_value,
    is_hexadecimal,
    pairwise
)

value_to_iterable_value_parameters = {
    0: {
        "value": 'foo',
        "return_value": ['foo']
    },
    1: {
        "value": 'foo',
        "output_iterable_type": list,
        "return_value": ['foo']
    },
    2: {
        "value": 'foo',
        "output_iterable_type": tuple,
        "return_value": ('foo',)
    },
    3: {
        "value": 'foo',
        "output_iterable_type": set,
        "return_value": {'foo'}
    },
    4: {
        "value": ['foo'],
        "return_value": ['foo']
    },
    5: {
        "value": ('foo',),
        "return_value": ['foo']
    },
    6: {
        "value": {'foo'},
        "return_value": ['foo']
    },
    7: {
        "value": ['foo'],
        "output_iterable_type": tuple,
        "return_value": ('foo',)
    },
    8: {
        "value": ('foo',),
        "output_iterable_type": tuple,
        "return_value": ('foo',)
    },
    9: {
        "value": {'foo'},
        "output_iterable_type": tuple,
        "return_value": ('foo',)
    },
    10: {
        "value": ['foo'],
        "output_iterable_type": set,
        "return_value": {'foo'}
    },
    11: {
        "value": ('foo',),
        "output_iterable_type": set,
        "return_value": {'foo'}
    },
    12: {
        "value": {'foo'},
        "output_iterable_type": set,
        "return_value": {'foo'}
    },
    13: {
        "value": ['foo', 'bar'],
        "output_iterable_type": set,
        "return_value": {'foo', 'bar'}
    },
    14: {
        "value": ('foo', 'bar'),
        "output_iterable_type": set,
        "return_value": {'foo', 'bar'}
    },
    15: {
        "value": {'foo', 'bar'},
        "output_iterable_type": set,
        "return_value": {'bar', 'foo'}
    },
    16: {
        "value": ['foo', 'bar'],
        "output_iterable_type": tuple,
        "return_value": ('foo', 'bar')
    },
    17: {
        "value": ('foo', 'bar'),
        "output_iterable_type": tuple,
        "return_value": ('foo', 'bar')
    },
    18: {
        "value": ['foo', 'bar'],
        "output_iterable_type": list,
        "return_value": ['foo', 'bar']
    },
    19: {
        "value": ('foo', 'bar'),
        "output_iterable_type": list,
        "return_value": ['foo', 'bar']
    },

}

is_hexadecimal_parameters = {
    0: {
        "s": "Hello world",
        "return_value": False
    },
    1: {
        "s": '1234567890',
        "return_value": True
    },
    2: {
        "s": "ABCDEFabcdef",
        "return_value": True
    },
    3: {
        "s": "ABCDEFabcdef1234567890",
        "return_value": True
    },
    4: {
        "s": "ABCDEFabcdef1234567890_",
        "return_value": False
    },
}

pairwise_parameters = {
    0: {
        "iterable": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "return_value": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    },
    1: {
        "iterable": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
        "return_value": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    }
}

def test_all():
    # value_to_iterable_value
    print(test_function(value_to_iterable_value, value_to_iterable_value_parameters))

    # is hexadecimal
    print(test_function(is_hexadecimal, is_hexadecimal_parameters))

    # pairwise
    print(test_function(pairwise, pairwise_parameters))


if __name__ == '__main__':
    test_all()