from __future__ import annotations

import functools as fn
from dataclasses import Field, dataclass, fields
from typing import Any, Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


def names(x) -> Iterator[str]:
    """The names of fields of the dataclass.

    This function iterates over fields in the same order as `values`.

    Parameters
    ----------

    x
        The dataclass (class or instance) we extract names from.

    Returns
    -------

    The names of all the fields of the dataclass.

    Examples
    --------

    If we define a dataclass with fields `x` and `y`,

    >>> @dataclass
    ... class Point(Generic[T]):
    ...     x: T
    ...     y: T

    then we can get the names `x` and `y` from either the class

    >>> list(names(Point))
    ['x', 'y']

    or an instance of the class

    >>> list(names(Point(1, 2)))
    ['x', 'y']

    """

    return (field.name for field in fields(x))


def values(x) -> Iterator[Any]:
    """The values of fields of the dataclass.

    This function iterates over the fields in the same order as
    `names`.

    Parameters
    ----------

    x
        The dataclass instance to extract values from.

    Returns
    -------

    The values stored in the dataclass.

    Examples
    --------

    If we define a dataclass with fields `x` and `y`,

    >>> @dataclass
    ... class Point(Generic[T]):
    ...     x: T
    ...     y: T

    we can access all values stored in an instance of the class:

    >>> list(values(Point(1, 2)))
    [1, 2]

    Note that unlike `names`, we cannot call `values` on the class
    itself:

    >>> list(values(Point))
    Traceback (most recent call last):
    ...
    AttributeError: type object 'Point' has no attribute 'x'

    """

    return (getattr(x, field.name) for field in fields(x))


def pure(x, z):
    """Construct a dataclass where every field contains the given value.

    Parameters
    ----------

    x
        The type (or instance of the type) to construct.
    z
        The constant value to put in each field.

    Returns
    -------

    An instance of the dataclass with all fields initialized to
    contain the given value.

    Examples
    --------

    If we define a dataclass with fields `x` and `y`,

    >>> @dataclass
    ... class Point(Generic[T]):
    ...     x: T
    ...     y: T

    we can construct an instance of the class containing a single value:

    >>> pure(Point, 1)
    Point(x=1, y=1)

    """

    # Handle being passed either a class or instance of a class
    type_x = type(x)
    cls = type_x if type_x is not type else x

    return cls(**{name: z for name in names(x)})


def fmap(f: Callable, x, *xs):
    """Apply a function to each field of a dataclass.

    The results are gathered into a new instance of the dataclass. If
    the function takes additional arguments, they can be provided by
    passing in additional arguments to this function.

    Parameters
    ----------

    f
        The function to apply to each field.

    x
        The dataclass to apply the function to; its fields will be the
        first positional argument to `f`.

    xs
        Additional dataclasses whose fields will be provided as
        additional positional arguments to `f`

    Returns
    -------

    A dataclass containing the results of each function evaluation.

    Examples
    --------

    If we define a dataclass with fields `x` and `y`,

    >>> @dataclass
    ... class Point(Generic[T]):
    ...     x: T
    ...     y: T

    we can apply functions to each attribute separately:

    >>> fmap('{:.2f}'.format, Point(1.111, 2.222))
    Point(x='1.11', y='2.22')

    If we want to apply a function with more than one argument, we can
    supply additional class instances as arguments:

    >>> import operator
    >>> fmap(operator.add, Point(1, 2), Point(3, 4))
    Point(x=4, y=6)

    """

    return amap(pure(x, f), x, *xs)


def amap(fs, *args):
    """Apply functions stored in one dataclass to values stored in others.

    The functions in the `fs` dataclass will be supplied position
    arguments from the fields of those in `args`.

    Parameters
    ----------

    fs
        The functions to evaluate.

    args
        Dataclasses containing the positional arguments to the
        functions in `fs`.

    Returns
    -------

    A dataclass containing the results of each function evaluation.

    Examples
    --------

    If we define a dataclass with fields `x` and `y`,

    >>> @dataclass
    ... class Point(Generic[T]):
    ...     x: T
    ...     y: T

    we can store functions in each attribute and apply those functions
    to values stored in the attributes of other instances:

    >>> import operator
    >>> amap(Point(operator.add, operator.sub), Point(1, 2), Point(3, 4))
    Point(x=4, y=-2)

    """

    return type(fs)(
        **{
            name: f(*xs)
            for name, f, *xs in zip(names(fs), values(fs), *map(values, args))
        }
    )


def gather(x, *xs):
    """Collect all fields from a list of dataclasses into a single
    instance.

    The requirement to have at least one positional argument is due to
    the necessity of having at least one instance from which we can
    construct the final dataclass. While it would be nice for
    `gather()` to create a dataclass containing the empty tuple in
    each field, we would have no way to know which dataclass to
    create. Use `pure(cls, (,))` if you need this behavior.

    Parameters
    ----------

    x
        The first object to collect

    xs
        The remaining objects to collect

    Returns
    -------

    A dataclass whose fields contain all the values from the provided
    instances.

    Examples
    --------

    If we define a dataclass with fields `x` and `y`,

    >>> @dataclass
    ... class Point(Generic[T]):
    ...     x: T
    ...     y: T

    we can collect all `x` and `y` values from a sequence of `Points`:

    >>> points = map(Point, range(0, 5), range(5, 10))
    >>> gather(*points)
    Point(x=(0, 1, 2, 3, 4), y=(5, 6, 7, 8, 9))

    """

    return fmap(lambda *args: tuple(args), x, *xs)
