import typing
import numpy as np
import functools
import tfields.lib.util


def ensure_complex(*base_vectors) -> typing.List[typing.Tuple[float, float, complex]]:
    """
    Ensure, that the third entry in base_vector of type tuple becomes a complex type.
    The first two are mapped to float if they they are complex but with imag == 0.
    """
    base_vectors = list(base_vectors)
    for i, vector in enumerate(base_vectors):
        if isinstance(vector, tuple):
            if len(vector) == 3:
                new_vector = []
                for j, entry in enumerate(vector):
                    # vector -> start, stop, n_steps
                    if isinstance(entry, complex) and entry.imag == 0:
                        # start and stop mapping to float
                        entry = entry.real
                    if j == 2:
                        # n_steps mapping to complex
                        if not isinstance(entry, complex):
                            entry = complex(0, entry)
                        elif entry.imag == 0:
                            entry = complex(0, entry.real)
                    new_vector.append(entry)
                base_vectors[i] = tuple(new_vector)
    return base_vectors


def to_base_vectors(*base_vectors):
    """
    Transform tuples to arrays with np.mgrid
    Args:
        tuple of lenght 3 with complex third entry -> start, stop, n_steps
    Returns:
        list if np.array for each base
    """
    base_vectors = list(base_vectors)
    # transform tuples to arrays with mgrid
    for i in range(len(base_vectors)):
        if isinstance(base_vectors[i], tuple):
            base_vectors[i] = np.mgrid[slice(*base_vectors[i])]
        if isinstance(base_vectors[i], list):
            base_vectors[i] = np.array(base_vectors[i])
    return base_vectors


def igrid(*base_vectors, **kwargs):
    """
    Args:
        *base_vectors (tuple, list or np.array): base vectors spaning the grid
            behaviour for different input types:
                tuple: will be transformed to slices and given to np.mgrid
                list or np.array: arbitrary base vectors
        **kwargs
            iter_order (list): order in which the iteration will be done.
                Frequency rises with position in list. default is [0, 1, 2]
                iteration will be done like::

                for v0 in base_vectors[iter_order[0]]:
                    for v1 in base_vectors[iter_order[1]]:
                        for v2 in base_vectors[iter_order[2]]:
                            ...

    Examples:
        Initilaize using the mgrid notation
        >>> import tfields
        >>> import numpy as np
        >>> assert np.array_equal(tfields.lib.grid.igrid((0, 1, 2j),
        ...                                              (3, 4, 2j),
        ...                                              (6, 7, 2j)),
        ...                       [[ 0.,  3.,  6.],
        ...                        [ 0.,  3.,  7.],
        ...                        [ 0.,  4.,  6.],
        ...                        [ 0.,  4.,  7.],
        ...                        [ 1.,  3.,  6.],
        ...                        [ 1.,  3.,  7.],
        ...                        [ 1.,  4.,  6.],
        ...                        [ 1.,  4.,  7.]])

        >>> assert np.array_equal(tfields.lib.grid.igrid([3, 4],
        ...                                              np.linspace(0, 1, 2),
        ...                                              (6, 7, 2),
        ...                                     iter_order=[1, 0, 2]),
        ...                       [[ 3.,  0.,  6.],
        ...                        [ 3.,  0.,  7.],
        ...                        [ 4.,  0.,  6.],
        ...                        [ 4.,  0.,  7.],
        ...                        [ 3.,  1.,  6.],
        ...                        [ 3.,  1.,  7.],
        ...                        [ 4.,  1.,  6.],
        ...                        [ 4.,  1.,  7.]])
        >>> assert np.array_equal(tfields.lib.grid.igrid(np.linspace(0, 1, 2),
        ...                                              np.linspace(3, 4, 2),
        ...                                              np.linspace(6, 7, 2),
        ...                                              iter_order=[2, 0, 1]),
        ...                       [[ 0.,  3.,  6.],
        ...                        [ 0.,  4.,  6.],
        ...                        [ 1.,  3.,  6.],
        ...                        [ 1.,  4.,  6.],
        ...                        [ 0.,  3.,  7.],
        ...                        [ 0.,  4.,  7.],
        ...                        [ 1.,  3.,  7.],
        ...                        [ 1.,  4.,  7.]])

    """
    iter_order = kwargs.pop("iter_order", np.arange(len(base_vectors)))
    base_vectors = ensure_complex(*base_vectors)

    # create the grid
    if all([isinstance(val, tuple) for val in base_vectors]):
        base_vectors = [slice(*base_vectors[index]) for index in iter_order]
        obj = np.mgrid[base_vectors]
        obj = obj.reshape(obj.shape[0], -1).T
    else:
        base_vectors = to_base_vectors(*base_vectors)

        obj = np.empty(
            shape=(
                functools.reduce(lambda x, y: x * y, map(len, base_vectors)),
                len(base_vectors),
            )
        )

        def loop_rec(y, n_max, i=0, n=None, *vals):
            if n is None:
                n = n_max
            if n > 0:
                for val in y[n_max - n]:
                    i = loop_rec(y, n_max, i, n - 1, val, *vals)
            else:
                obj[i] = list(reversed(vals))
                i += 1
            return i

        loop_rec([base_vectors[i] for i in iter_order], len(base_vectors))

    swap_indices = compare_permutations(iter_order, np.arange(len(base_vectors)))
    swap_columns(obj, *swap_indices)
    return obj


def base_vectors(array, rtol=None, atol=None):
    """
    describe the array in terms of base vectors
    Inverse function of igrid

    Examples:
        >>> import tfields
        >>> grid = tfields.lib.grid.igrid((3, 5, 5j))
        >>> tfields.lib.grid.base_vectors(grid[:, 0])
        (3.0, 5.0, 5j)
        >>> grid2 = tfields.lib.grid.igrid((3, 5, 5j),
        ...                                (1, 2, 2j))
        >>> grid_circle = tfields.lib.grid.igrid(
        ...     *tfields.lib.grid.base_vectors(grid2))
        >>> assert tfields.Tensors(grid_circle).equal(grid2)

    """
    if len(array.shape) == 1:
        values = set(array)
        if rtol is not None and atol is not None:
            duplicates = set([])
            for v1, v2 in tfields.lib.util.pairwise(sorted(values)):
                if np.isclose(v1, v2, rtol=rtol, atol=atol):
                    duplicates.add(v2)
            values = values.difference(duplicates)
            # round to given absolute precision
            n_digits = int(abs(np.log10(atol))) + 1
            values = {round(v, n_digits) for v in values}
        elif rtol is not None or atol is not None:
            raise ValueError("rtol and atol arguments only come in pairs.")
        spacing = complex(0, len(values))
        vmin = min(values)
        vmax = max(values)
        return (vmin, vmax, spacing)
    elif len(array.shape) == 2:
        bases = []
        for i in range(array.shape[1]):
            bases.append(base_vectors(array[:, i], rtol=rtol, atol=atol))
        return bases
    else:
        raise NotImplementedError("Description yet only till rank 1")


def swap_columns(array, *index_tuples):
    """
    Args:
        array (list or array)
        expects tuples with indices to swap as arguments

    Examples:
        >>> import tfields
        >>> l = np.array([[3, 2, 1, 0], [6, 5, 4, 3]])
        >>> tfields.lib.grid.swap_columns(l, (1, 2), (0, 3))
        >>> l
        array([[0, 1, 2, 3],
               [3, 4, 5, 6]])
    """
    # test swap_indices type
    for si in index_tuples:
        if hasattr(si, "__iter__"):
            if len(si) == 2:
                continue
        raise TypeError("swap_indices must be tuple but is {}".format(si))
    for i, j in index_tuples:
        array[:, [i, j]] = array[:, [j, i]]


def swap_rows(array, *args):
    """
    Args:
        array (list)
        expects tuples with indices to swap as arguments

    Examples:
        >>> import tfields
        >>> l = [[3,3,3], [2,2,2], [1,1,1], [0, 0, 0]]
        >>> tfields.lib.grid.swap_rows(l, (1, 2), (0, 3))
        >>> l
        [[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3]]
    """
    for i, j in args:
        array[i], array[j] = array[j], array[i]


def compare_permutations(permut1, permut2):
    """
    Return what rows you need to switch in order to make permut1 become permut2

    Examples:
        >>> import tfields
        >>> a = [1, 2, 0, 4, 3]
        >>> b = [0, 1, 2, 3, 4]
        >>> si = tfields.lib.grid.compare_permutations(a, b)
        >>> si
        [(0, 2), (1, 2), (3, 4)]
        >>> tfields.lib.grid.swap_rows(a, *si)
        >>> a
        [0, 1, 2, 3, 4]
        >>> a == b
        True
    """
    swap_indices = []
    permut1 = list(permut1)
    i = 0
    while i < len(permut2):
        if not permut1[i] == permut2[i]:
            j = permut1.index(permut2[i])
            swap_rows(permut1, (i, j))
            swap_indices.append((i, j))
        i += 1
    return swap_indices


def change_iter_order(
    bv_lengths: typing.List[int],
    iter_order: typing.List[int],
    iter_order_new: typing.List[int],
):
    """
    Args:
        bv_lengths: lenghts of basis vectors


    Returns:
        indices for changeing fields generated with iter_order to iter_order_new
    """
    indices = np.arange(np.prod(bv_lengths))
    shape = []
    for i in iter_order:
        shape.append(bv_lengths[i])
    indices = indices.reshape(shape)
    # swaps = compare_permutations(iter_order_new, iter_order)
    swaps = compare_permutations(iter_order, iter_order_new)
    # swaps = compare_permutations(iter_order_new, np.arange(len(iter_order)))
    for swap in swaps:
        indices = np.swapaxes(indices, swap[0], swap[1])
    # indices = np.transpose(indices, axes=axes_transp)
    return np.array(indices.flat)
