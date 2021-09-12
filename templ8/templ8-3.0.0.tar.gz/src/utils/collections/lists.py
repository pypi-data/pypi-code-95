from typing import Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")  # pylint: disable = C0103
U = TypeVar("U")  # pylint: disable = C0103


def sieve(
    lst: List[T],
    lookup: Callable[[T], U],
    includes: Optional[List[U]] = None,
    excludes: Optional[List[U]] = None,
) -> List[T]:
    """
    >>> sieve([1, 2, 3], lambda x: x)
    [1, 2, 3]

    >>> sieve([1, 2, 3], lambda x: x, None)
    [1, 2, 3]

    >>> sieve([1, 2, 3], lambda x: x, [])
    []

    >>> sieve([1, 2, 3], lambda x: x, [1, 2])
    [1, 2]

    >>> sieve([1, 2, 3], lambda x: x, [])
    []

    >>> sieve([1, 2, 3], lambda x: x, None, [3])
    [1, 2]

    >>> sieve([1, 2, 3], lambda x: x, [1, 2], [2, 3])
    [1]

    >>> sieve([1, 2, 3], lambda x: str(x), ['1', '2'], None)
    [1, 2]
    """

    return list(
        filter(
            lambda x: (includes is None or lookup(x) in includes)
            and (excludes is None or lookup(x) not in excludes),
            lst,
        )
    )


def group_by(arr: List[T], attr: str) -> Dict[str, List[T]]:
    """
    >>> group_by(['a', 1, 'b', 2], '__class__')
    {<class 'str'>: ['a', 'b'], <class 'int'>: [1, 2]}
    """
    groups = {}  # type: Dict[str, List[T]]

    for i in arr:
        k = getattr(i, attr) if hasattr(i, attr) else None

        if k in groups:
            groups[k].append(i)

        else:
            groups[k] = [(i)]

    return groups


def sort_with(lst: List[T], ref: List[U], lookup: Callable[[T], U]) -> List[T]:
    """
    >>> sort_with([1, 2, 3], [1, 3, 2], lambda x: x)
    [1, 3, 2]

    >>> sort_with([1, 2, 3], [1, 3], lambda x: x)
    [1, 3, 2]

    >>> sort_with([1, 2, 3], [1], lambda x: x)
    [1, 2, 3]

    >>> sort_with([1, 2, 3], [4, 1, 3, 5], lambda x: x)
    [1, 3, 2]
    """
    index = lambda x: ref.index(lookup(x)) if lookup(x) in ref else len(lst)
    return sorted(lst, key=index)
