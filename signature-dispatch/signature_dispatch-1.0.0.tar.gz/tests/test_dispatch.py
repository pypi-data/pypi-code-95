#!/usr/bin/env python3

import signature_dispatch as sd, pytest
from typing import List, Callable

@pytest.fixture(autouse=True, params=[False, True])
def currentframe(request, monkeypatch):
    # Not all python implementations support `inspect.currentframe()`, so run 
    # every test with and without it.
    if request.param:
        import inspect
        monkeypatch.setattr(inspect, 'currentframe', lambda: None)


def test_positional_or_keyword():

    @sd
    def f(a):
        return a

    @sd
    def f(a, b):
        return a, b

    assert f(1) == 1
    assert f(a=1) == 1

    assert f(1, 2) == (1, 2)
    assert f(1, b=2) == (1, 2)
    assert f(a=1, b=2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1, 2, 3)

def test_var_positional():

    @sd
    def f(*a):
        return a

    @sd
    def f(*a, b):
        return a, b

    assert f() == ()
    assert f(1) == (1,)
    assert f(1, 2) == (1, 2)

    assert f(b=1) == ((), 1)
    assert f(1, b=2) == ((1,), 2)
    assert f(1, 2, b=3) == ((1, 2), 3)

    with pytest.raises(TypeError):
        f(c=1)

def test_keyword_only():

    @sd
    def f(*, a):
        return a

    @sd
    def f(*, a, b):
        return a, b

    assert f(a=1) == 1
    assert f(a=1, b=2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1)
    with pytest.raises(TypeError):
        f(b=1)

def test_var_keyword():

    @sd
    def f(**kwargs):
        return kwargs

    @sd
    def f(a, **kwargs):
        return a, kwargs

    assert f() == {}
    assert f(a=1) == {'a': 1}
    assert f(b=1) == {'b': 1}
    assert f(a=1, b=2) == {'a': 1, 'b': 2}

    assert f(1) == (1, {})
    assert f(1, b=2) == (1, {'b': 2})
    assert f(1, c=2) == (1, {'c': 2})
    assert f(1, b=2, c=3) == (1, {'b': 2, 'c': 3})

    with pytest.raises(TypeError):
        f(1, 2)
    with pytest.raises(TypeError):
        f(1, a=2)  # `a` specified twice

def test_annotation():

    @sd
    def f(a: int):
        return 'int', a

    @sd
    def f(a: str):
        return 'str', a

    @sd
    def f(a: List[int]):
        return 'List[int]', a

    @sd
    def f(a: Callable):
        return 'Callable', a

    assert f(1) == ('int', 1)
    assert f('a') == ('str', 'a')
    assert f([]) == ('List[int]', [])
    assert f([1]) == ('List[int]', [1])
    assert f(max) == ('Callable', max)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f({})
    with pytest.raises(TypeError):
        f(['a'])

def test_annotation_default():

    @sd
    def f(a: int=0):
        return 'int', a

    @sd
    def f(a: str):
        return 'str', a

    assert f() == ('int', 0)
    assert f(1) == ('int', 1)
    assert f('a') == ('str', 'a')

def test_annotation_var_positional():

    @sd
    def f(*a: int):
        return 'int', a

    @sd
    def f(*a: str):
        return 'str', a

    assert f() == ('int', ())
    assert f(1) == ('int', (1,))
    assert f(1, 2) == ('int', (1, 2))
    assert f('a') == ('str', ('a',))
    assert f('a', 'b') == ('str', ('a', 'b'))

def test_annotation_var_keyword():

    @sd
    def f(**a: int):
        return 'int', a

    @sd
    def f(**a: str):
        return 'str', a

    assert f() == ('int', {})
    assert f(a=1) == ('int', {'a': 1})
    assert f(a=1, b=2) == ('int', {'a': 1, 'b': 2})
    assert f(a='a') == ('str', {'a': 'a'})
    assert f(a='a', b='b') == ('str', {'a': 'a', 'b': 'b'})

def test_method():

    class C:

        @sd
        def m(self, a):
            return a

        @sd
        def m(self, a, b):
            return a, b

    obj = C()

    assert obj.m(1) == 1
    assert obj.m(1, 2) == (1, 2)

    with pytest.raises(TypeError):
        obj.m()
    with pytest.raises(TypeError):
        obj.m(1, 2, 3)

def test_classmethod():

    class C:

        @sd
        def m(cls, a):
            return cls, a

        @sd
        def m(cls, a, b):
            return cls, a, b

        m = classmethod(m)

    obj = C()

    assert obj.m(1) == (C, 1)
    assert obj.m(1, 2) == (C, 1, 2)

    with pytest.raises(TypeError):
        obj.m()
    with pytest.raises(TypeError):
        obj.m(1, 2, 3)

@pytest.mark.parametrize(
        'deco_a,deco_b,expected', [
            (sd,              sd,              'a'),

            (sd(priority=1),  sd,              'a'),
            (sd,              sd(priority=1),  'b'),
            (sd(priority=1),  sd(priority=1),  'a'),

            (sd(priority=-1), sd,              'b'),
            (sd,              sd(priority=-1), 'a'),
            (sd(priority=-1), sd(priority=-1), 'a'),

            (sd(priority=1),  sd(priority=-1), 'a'),
            (sd(priority=-1), sd(priority=1),  'b'),
        ],
)
def test_priority(deco_a, deco_b, expected):

    @deco_a
    def f():
        return 'a'

    @deco_b
    def f():
        return 'b'

    assert f() == expected

def test_overload():

    @sd
    def f(a):
        return a

    @f.overload
    def _(a, b):
        return a, b

    assert f(1) == 1
    assert f(1, 2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1, 2, 3)

@pytest.mark.parametrize(
        'priority, expected', [
            (-1, 'a'),
            (0, 'a'),
            (1, 'b'),
        ],
)
def test_overload_priority(priority, expected):

    @sd
    def f():
        return 'a'

    @f.overload(priority=priority)
    def _():
        return 'b'

    assert f() == expected

def test_docstring():

    @sd
    def f(a):
        "a"
        return a

    @sd
    def f(a, b):
        "a, b"
        return a, b

    assert f.__doc__ == "a"

def test_error_message():

    @sd
    def f(a):
        return a

    @sd
    def f(a, b):
        return a, b

    with pytest.raises(TypeError) as err:
        f()

    assert err.match(r"(?m)can't dispatch the given arguments to any of the candidate functions:")
    assert err.match(r"(?m)arguments: $")
    assert err.match(r"(?m)candidates:$")
    assert err.match(r"(?m)\(a\): missing a required argument: 'a'$")
    assert err.match(r"(?m)\(a, b\): missing a required argument: 'a'$")

    with pytest.raises(TypeError) as err:
        f(1, 2, 3)

    assert err.match(r"(?m)can't dispatch the given arguments to any of the candidate functions:")
    assert err.match(r"(?m)arguments: 1, 2, 3$")
    assert err.match(r"(?m)candidates:$")
    assert err.match(r"(?m)\(a\): too many positional arguments$")
    assert err.match(r"(?m)\(a, b\): too many positional arguments$")

def test_error_message_annotation():

    @sd
    def f(a: int):
        return a

    @sd
    def f(a: List[int]):
        return a

    with pytest.raises(TypeError) as err:
        f('a')

    assert err.match(r"(?m)can't dispatch the given arguments to any of the candidate functions:")
    assert err.match(r"(?m)arguments: 'a'$")
    assert err.match(r"(?m)candidates:$")
    assert err.match(r"(?m)\(a: ?int\): type of a must be int; got str instead$")
    assert err.match(r"(?m)\(a: ?List\[int\]\): type of a must be a list; got str instead$")

    with pytest.raises(TypeError) as err:
        f(['a'])

    assert err.match(r"(?m)can't dispatch the given arguments to any of the candidate functions:")
    assert err.match(r"(?m)arguments: \['a'\]$")
    assert err.match(r"(?m)candidates:$")
    assert err.match(r"(?m)\(a: ?int\): type of a must be int; got list instead$")
    assert err.match(r"(?m)\(a: ?List\[int\]\): type of a\[0\] must be int; got str instead$")

def test_function_raises_type_error():

    @sd
    def f(a):
        raise TypeError("my error")

    @sd
    def f(a):
        return a

    with pytest.raises(TypeError, match="my error"):
        f(1)

def test_ignore_local_variables_with_same_name():
    f = None

    @sd
    def f(a):
        return a

    @sd
    def f(a, b):
        return a, b

    assert f(1) == 1
    assert f(1, 2) == (1, 2)

    with pytest.raises(TypeError):
        f()
    with pytest.raises(TypeError):
        f(1, 2, 3)

