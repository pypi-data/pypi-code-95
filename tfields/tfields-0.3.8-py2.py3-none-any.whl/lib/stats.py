#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

part of tfields library
"""
import numpy as np
import scipy
import scipy.stats
import logging


def mode(array, axis=0, bins='auto', range=None):
    """
    generalisation of the scipy.stats.mode function for floats with binning
    Examples:
        Forwarding usage:
        >>> import tfields  # NOQA
        >>> import numpy as np
        >>> tfields.lib.stats.mode([[2,2,3], [4,5,3]])
        array([[2, 2, 3]])
        >>> tfields.lib.stats.mode([[2,2,3], [4,5,3]], axis=1)
        array([[2],
               [3]])

        Float usage:
        >>> np.random.seed(seed=0)  # deterministic random
        >>> n = np.random.normal(3.1, 2., 1000)
        >>> assert np.isclose(tfields.lib.stats.mode(n), [ 2.30838613])
        >>> assert np.isclose(tfields.lib.stats.mode(n, bins='sturges'),
        ...                   [ 2.81321206])
        >>> assert np.allclose(tfields.lib.stats.mode(np.array([n, n]), axis=1),
        ...                    [[ 2.30838613],
        ...                     [ 2.30838613]])
        >>> tfields.lib.stats.mode(np.array([n, n]), axis=0).shape
        (1000, 1)
        >>> tfields.lib.stats.mode(np.array([n, n]), axis=1).shape
        (2, 1)
        >>> assert np.isclose(tfields.lib.stats.mode(np.array([n, n]),
        ...                                          axis=None),
        ...                   [ 2.81321206])

    """
    array = np.asarray(array)
    if issubclass(array.dtype.type, np.integer):
        return scipy.stats.mode(array, axis=axis).mode

    # hack only works for 2 dimensional arrays
    if len(array.shape) > 2:
        raise NotImplementedError("Only dimensions <= 2 allowed")

    if len(array.shape) == 2:
        if axis is None:
            array = array.reshape(array.size)
            return mode(array, axis=0, bins=bins, range=range)
        if axis == 0:
            array = array.T
        return np.array([mode(a, axis=0, bins=bins, range=range) for a in array])

    # only 1 d arrays remaining
    if not (axis is None or axis == 0):
        raise NotImplementedError("Axis is not None or 0 but {0}".format(axis))

    hist, binEdges = np.histogram(array, bins)
    maxIndex = hist.argmax(axis=axis)
    return np.array([0.5 * (binEdges[maxIndex] + binEdges[maxIndex + 1])])


mean = np.mean
median = np.median


def _chk_asarray(a, axis):
    """
    copied from scipy.stats
    """
    if axis is None:
        a = np.ravel(a)
        outaxis = 0
    else:
        a = np.asarray(a)
        outaxis = axis

    if a.ndim == 0:
        a = np.atleast_1d(a)

    return a, outaxis


def _contains_nan(a, nan_policy='propagate'):
    """
    copied from scipy.stats
    """
    policies = ['propagate', 'raise', 'omit']
    if nan_policy not in policies:
        raise ValueError("nan_policy must be one of {%s}" %
                         ', '.join("'%s'" % s for s in policies))
    try:
        # Calling np.sum to avoid creating a huge array into memory
        # e.g. np.isnan(a).any()
        with np.errstate(invalid='ignore'):
            contains_nan = np.isnan(np.sum(a))
    except TypeError:
        # If the check cannot be properly performed we fallback to omitting
        # nan values and raising a warning. This can happen when attempting to
        # sum things that are not numbers (e.g. as in the function `mode`).
        contains_nan = False
        nan_policy = 'omit'
        logging.warning("The input array could not be properly checked for nan"
                        " values. nan values will be ignored.")

    if contains_nan and nan_policy == 'raise':
        raise ValueError("The input contains nan values")

    return (contains_nan, nan_policy)


def moment(a, moment=1, axis=0, weights=None, nan_policy='propagate'):
    r"""
    Calculate the nth moment about the mean for a sample.
    A moment is a specific quantitative measure of the shape of a set of
    points. It is often used to calculate coefficients of skewness and kurtosis
    due to its close relationship with them.
    Parameters
    ----------
    a : array_like
       data
    moment : int or array_like of ints, optional
       order of central moment that is returned. Default is 1.
    axis : int or None, optional
       Axis along which the central moment is computed. Default is 0.
       If None, compute over the whole array `a`.
    nan_policy : {'propagate', 'raise', 'omit'}, optional
        Defines how to handle when input contains nan. 'propagate' returns nan,
        'raise' throws an error, 'omit' performs the calculations ignoring nan
        values. Default is 'propagate'.
    Returns
    -------
    n-th central moment : ndarray or float
       The appropriate moment along the given axis or over all values if axis
       is None. The denominator for the moment calculation is the number of
       observations, no degrees of freedom correction is done.
    See also
    --------
    kurtosis, skew, describe
    Notes
    -----
    The k-th weighted central moment of a data sample is:
    .. math::
        m_k = \frac{1}{\sum_{j = 1}^n w_i} \sum_{i = 1}^n w_i (x_i - \bar{x})^k
    Where n is the number of samples and x-bar is the mean. This function uses
    exponentiation by squares [1]_ for efficiency.
    References
    ----------
    .. [1] http://eli.thegreenplace.net/2009/03/21/efficient-integer-exponentiation-algorithms
    Examples
    --------
    >>> from tfields.lib.stats import moment
    >>> moment([1, 2, 3, 4, 5], moment=0)
    1.0
    >>> moment([1, 2, 3, 4, 5], moment=1)
    0.0
    >>> moment([1, 2, 3, 4, 5], moment=2)
    2.0

    Expansion of the scipy.stats moment function by weights:
    >>> moment([1, 2, 3, 4, 5], moment=1, weights=[-2, -1, 20, 1, 2])
    0.5

    >>> moment([1, 2, 3, 4, 5], moment=2, weights=[5, 4, 3, 2, 1])
    2.0
    >>> moment([1, 2, 3, 4, 5], moment=2, weights=[5, 4, 3, 2, 1])
    2.0
    >>> assert moment([1, 2, 3, 4, 5], moment=2,
    ...               weights=[0.25, 1, 17.5, 1, 0.25]) == 0.2
    >>> moment([1, 2, 3, 4, 5], moment=2, weights=[0, 0, 1, 0, 0])
    0.0

    """
    a, axis = _chk_asarray(a, axis)

    contains_nan, nan_policy = _contains_nan(a, nan_policy)

    if contains_nan and nan_policy == 'omit':
        a = a.masked_invalid(a)
        return scipy.mstats_basic.moment(a, moment, axis)

    if a.size == 0:
        # empty array, return nan(s) with shape matching `moment`
        if np.isscalar(moment):
            return np.nan
        else:
            return np.ones(np.asarray(moment).shape, dtype=np.float64) * np.nan

    # for array_like moment input, return a value for each.
    if not np.isscalar(moment):
        mmnt = [_moment(a, i, axis, weights=weights) for i in moment]
        return np.array(mmnt)
    else:
        return _moment(a, moment, axis, weights=weights)


def _moment(a, moment, axis, weights=None):
    if np.abs(moment - np.round(moment)) > 0:
        raise ValueError("All moment parameters must be integers")

    if moment == 0:
        # When moment equals 0, the result is 1, by definition.
        shape = list(a.shape)
        del shape[axis]
        if shape:
            # return an actual array of the appropriate shape
            return np.ones(shape, dtype=float)
        else:
            # the input was 1D, so return a scalar instead of a rank-0 array
            return 1.0
    elif weights is None and moment == 1:
        # By definition the first moment about the mean is 0.
        shape = list(a.shape)
        del shape[axis]
        if shape:
            # return an actual array of the appropriate shape
            return np.zeros(shape, dtype=float)
        else:
            # the input was 1D, so return a scalar instead of a rank-0 array
            return np.float64(0.0)
    else:
        # Exponentiation by squares: form exponent sequence
        n_list = [moment]
        current_n = moment
        while current_n > 2:
            if current_n % 2:
                current_n = (current_n - 1) / 2
            else:
                current_n /= 2
            n_list.append(current_n)

        # Starting point for exponentiation by squares
        a_zero_mean = a - np.expand_dims(np.mean(a, axis), axis)
        if n_list[-1] == 1:
            s = a_zero_mean.copy()
        else:
            s = a_zero_mean**2

        # Perform multiplications
        for n in n_list[-2::-1]:
            s = s**2
            if n % 2:
                s *= a_zero_mean
    return np.average(s, axis, weights=weights)


if __name__ == '__main__':
    import doctest
    import tfields  # NOQA: F401
    doctest.testmod()
