import pytest

from parallely import parallel

convert = lambda func: parallel(func)


def test_empty(single_arg, multi_kwarg):
    single_arg, multi_kwarg = convert(single_arg), convert(multi_kwarg)

    with pytest.raises(TypeError):
        assert single_arg()

    with pytest.raises(TypeError):
        multi_kwarg()


def test_normal_call(single_arg, multi_kwarg):
    single_arg, multi_kwarg = convert(single_arg), convert(multi_kwarg)

    assert single_arg(1) == 1
    assert single_arg(a=1) == 1

    assert multi_kwarg(1, 1) == 2
    assert multi_kwarg(a=1, b=1) == 2
    assert multi_kwarg(1, b=1) == 2


def test_iterators_only(single_arg, multi_kwarg):
    single_arg, multi_kwarg = convert(single_arg), convert(multi_kwarg)

    assert single_arg.map([1, 1]) == [1, 1]
    assert single_arg.map(a=[1, 1]) == [1, 1]

    assert multi_kwarg.map([1, 1], [1, 1]) == [2, 2]
    assert multi_kwarg.map(a=[1, 1], b=[1, 1]) == [2, 2]
    assert multi_kwarg.map([1, 1], b=[1, 1]) == [2, 2]


def test_iterators_and_constants(multi_kwarg):
    multi_kwarg = convert(multi_kwarg)

    assert multi_kwarg.map([1, 1], 1) == [2, 2]
    assert multi_kwarg.map(1, [1, 1]) == [2, 2]
    assert multi_kwarg.map(a=1, b=[1, 1]) == [2, 2]
    assert multi_kwarg.map(a=[1, 1], b=1) == [2, 2]
    assert multi_kwarg.map(1, b=[1, 1]) == [2, 2]
    assert multi_kwarg.map([1, 1], b=1) == [2, 2]


def test_uneven_iterators(multi_kwarg):
    multi_kwarg = convert(multi_kwarg)

    assert multi_kwarg.map([1, 1], [1]) == [2]
    assert multi_kwarg.map(a=[1, 1], b=[1]) == [2]
    assert multi_kwarg.map([1], b=[1, 1]) == [2]


def test_empty_iterators(multi_kwarg):
    multi_kwarg = convert(multi_kwarg)

    with pytest.raises(ValueError):
        assert multi_kwarg.map([1, 1], []) == [2]
    with pytest.raises(ValueError):
        assert multi_kwarg.map(a=[1, 1], b=[]) == [2]

    with pytest.raises(ValueError):
        assert multi_kwarg.map([], b=[1, 1]) == [2]
