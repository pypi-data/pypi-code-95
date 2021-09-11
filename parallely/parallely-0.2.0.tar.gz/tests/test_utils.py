from parallely.utils import prepare_arguments


def test_iterators_only():
    args, kwargs = prepare_arguments(([1, 2],), {})
    assert args == [[1], [2]]
    assert kwargs == [{}, {}]

    args, kwargs = prepare_arguments(([1, 2],), {"a": [3, 4]})
    assert args == [[1], [2]]
    assert kwargs == [{"a": 3}, {"a": 4}]


def test_iterators_and_constants():
    pass


def test_iterators_and_repeats():
    pass


def test_args_input():
    pass


def test_kwargs_input():
    pass
