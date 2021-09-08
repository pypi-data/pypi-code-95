"""
Various utility functions
"""
import itertools
from six import string_types
import numpy as np


def pairwise(iterable):
    """
    iterator s -> (s0,s1), (s1,s2), (s2, s3), ...
    Source:
        https://stackoverflow.com/questions/5434891/iterate-a-list-as-pair-current-next-in-python
    Returns:
        two iterators, one ahead of the other
    """
    # pylint:disable=invalid-name
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def flatten(seq, container=None, keep_types=None):
    """
    Approach to flatten a nested sequence.
    Args:
        seq (iterable): iterable to be flattened
        containter (iterable): iterable defining an append method. Values will
            be appended there
        keep_types (list of type): types that should not be flattened but kept
            in nested form
    Examples:
        >>> from tfields.lib.util import flatten
        >>> import numpy as np
        >>> flatten([[1,2,3],4,[[5,[6]]]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten([[1,2,3],4,[[5,[{6:1}]]]], keep_types=[dict])
        [1, 2, 3, 4, 5, {6: 1}]
        >>> flatten([[1,2,3],4,[[5,[np.array([6])]]]], keep_types=[np.ndarray])
        [1, 2, 3, 4, 5, array([6])]

        Strings work although they have the __iter__ attribute in python3
        >>> flatten([[0, 0, 0, 'A'], [1, 2, 3]])
        [0, 0, 0, 'A', 1, 2, 3]

    """
    if keep_types is None:
        keep_types = []
    if container is None:
        container = []
    # pylint:disable=invalid-name
    for s in seq:
        if (
            hasattr(s, "__iter__")
            and not isinstance(s, string_types)
            and not any((isinstance(s, t) for t in keep_types))
        ):
            flatten(s, container, keep_types)
        else:
            container.append(s)
    return container


def multi_sort(array, *others, **kwargs):
    """
    Sort all given lists parralel with array sorting, ie rearrange the items in
    the other lists in the same way, you rearrange them for array due to array
    sorting

    Args:
        array (iterable)
        *others (iterable)
        **kwargs:
            method (function): sorting function. Default is 'sorted'
            ...: further arguments are passed to method. Default rest is
                'key=array[0]'
            reversed (bool): wether to reverse the results or not
            cast_type (type): type of returned iterables

    Examples:
        >>> from tfields.lib.util import multi_sort
        >>> multi_sort([1,2,3,6,4], [1,2,3,4,5])
        ([1, 2, 3, 4, 6], [1, 2, 3, 5, 4])
        >>> a, b = multi_sort([1,2,3,6,4], [1,2,3,4,5])
        >>> b
        [1, 2, 3, 5, 4]

        Expanded to sort as many objects as needed
        >>> multi_sort([1,2,3,6,4], [1,2,3,4,5], [6,5,4,3,2])
        ([1, 2, 3, 4, 6], [1, 2, 3, 5, 4], [6, 5, 4, 2, 3])

        Reverse argument
        >>> multi_sort([1,2,3,6,4], [1,2,3,4,5], [6,5,4,3,2], reverse=True)
        ([6, 4, 3, 2, 1], [4, 5, 3, 2, 1], [3, 2, 4, 5, 6])

    Returns:
        tuple(cast_type): One iterable for each
        >>> multi_sort([], [], [])
        ([], [], [])
        >>> multi_sort([], [], [], cast_type=tuple)
        ((), (), ())

    """
    method = kwargs.pop("method", None)
    cast_type = kwargs.pop("cast_type", list)

    if len(array) == 0:
        return tuple(cast_type(x) for x in [array] + list(others))

    if method is None:
        method = sorted
        if "key" not in kwargs:
            kwargs["key"] = lambda pair: pair[0]

    reverse = kwargs.pop("reverse", False)
    if reverse:
        cast_type = lambda x: list(reversed(x))  # NOQA

    return tuple(cast_type(x) for x in zip(*method(zip(array, *others), **kwargs)))


def convert_nan(arr, value=0.0):
    """
    Replace all occuring NaN values by value
    """
    nan_indices = np.isnan(arr)
    arr[nan_indices] = value


def view_1d(arr):
    """
    Delete duplicate columns of the input array
    https://stackoverflow.com/a/44999009/ @Divakar
    """
    arr = np.ascontiguousarray(arr)
    coid_dt = np.dtype((np.void, arr.dtype.itemsize * arr.shape[1]))
    return arr.view(coid_dt).ravel()


def argsort_unique(idx):
    """
    https://stackoverflow.com/a/43411559/ @Divakar
    """
    num = idx.size
    sidx = np.empty(num, dtype=int)
    sidx[idx] = np.arange(num)
    return sidx


def duplicates(arr, axis=None):
    """
    View1D version of duplicate search
    Speed up version after
    https://stackoverflow.com/questions/46284660 \
        /python-numpy-speed-up-2d-duplicate-search/46294916#46294916

    Args:
        arr (array_like): array
        other args: see np.isclose

    Examples:
        >>> import tfields
        >>> import numpy as np
        >>> a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
        >>> tfields.lib.util.duplicates(a, axis=0)
        array([0, 0, 2])

        An empty sequence will not throw errors
        >>> assert np.array_equal(tfields.lib.util.duplicates([], axis=0), [])

    Returns:
        list of int: int is pointing to first occurence of unique value
    """
    if len(arr) == 0:
        return np.array([])
    if axis != 0:
        raise NotImplementedError()
    sidx = np.lexsort(arr.T)
    sorted_ = arr[sidx]

    group_index_0 = np.flatnonzero((sorted_[1:] != sorted_[:-1]).any(1)) + 1
    group_index = np.concatenate(([0], group_index_0, [sorted_.shape[0]]))
    ids = np.repeat(range(len(group_index) - 1), np.diff(group_index))
    sidx_mapped = argsort_unique(sidx)
    ids_mapped = ids[sidx_mapped]

    grp_minidx = sidx[group_index[:-1]]
    out = grp_minidx[ids_mapped]
    return out


# pylint:disable=too-many-arguments
def index(arr, entry, rtol=0, atol=0, equal_nan=False, axis=None):
    """
    Examples:
        >>> import tfields
        >>> a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
        >>> tfields.lib.util.index(a, [2, 3, 4], axis=0)
        2

        >>> a = np.array([[1, 0, 0], [2, 3, 4]])
        >>> tfields.lib.util.index(a, 4)
        5

    Returns:
        list of int: indices of point occuring
    """
    if axis is None:
        arr = arr.flatten()
    elif axis != 0:
        raise NotImplementedError()
    for i, part in enumerate(arr):
        isclose = np.isclose(part, entry, rtol=rtol, atol=atol, equal_nan=equal_nan)
        if axis is not None:
            isclose = isclose.all()
        if isclose:
            return i


def is_full_slice(index, shape):
    """
    Determine if an index is the full slice (i.e. __getitem__ with this index returns the full
    array) w.r.t the shape given.

    Examples:
        >>> import numpy as np
        >>> import tfields
        >>> class index_getter:
        ...     def __getitem__(self, index):
        ...         return index
        >>> get_index = index_getter()
        >>> a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
        >>> shape = a.shape
        >>> tfields.lib.util.is_full_slice(get_index[:], shape)
        True
        >>> tfields.lib.util.is_full_slice(get_index[:, :], shape)
        True
        >>> tfields.lib.util.is_full_slice(get_index[:, 1], shape)
        False
        >>> tfields.lib.util.is_full_slice(get_index[1:, :], shape)
        False
        >>> tfields.lib.util.is_full_slice(get_index[:1, :], shape)
        False
        >>> tfields.lib.util.is_full_slice(get_index[:, 1:], shape)
        False
        >>> tfields.lib.util.is_full_slice(get_index[:, :1], shape)
        False
        >>> tfields.lib.util.is_full_slice(get_index[:, :-1], shape)
        True
        >>> tfields.lib.util.is_full_slice(get_index[np.array([True, True, True])], shape)
        True
        >>> tfields.lib.util.is_full_slice(get_index[np.array([True, True, False])], shape)
        False
    """
    if isinstance(index, slice):
        if (
            index.step in (None, 1)
            and index.start in (None, 0)
            and index.stop in (None, -1, shape[0])
        ):
            # full slice -> no type change
            return True
        else:
            return False
    elif isinstance(index, tuple):
        return all((is_full_slice(ind, (shp,)) for ind, shp in zip(index, shape)))
    elif isinstance(index, int):
        return index == 0 and shape[0] == 1
    elif isinstance(index, (np.ndarray, list)):
        return all(index)
    else:
        raise NotImplementedError("Index Type %s", type(index))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
