from typing import Optional, Union

import numpy as np
from numpy import array, ascontiguousarray, float64, zeros
from numba import _helperlib, njit

import pandas as pd

from sklearn.model_selection import cross_validate, KFold, RandomizedSearchCV
from sklearn.utils import shuffle
from sksurv import metrics
from sksurv.util import Surv

from harmoniums.const import Matrix


class MiniBatchIterator:
    """
    Make mini-batch iterator of the data.
    """

    def __init__(
        self,
        *args: Matrix,
        mini_batch_size: Union[float, int] = 100,
        shuffle_data_once: bool = False,
        shuffle_each_epoch: bool = False,
        # The iterator is exhausted after this many epochs.
        number_of_epochs: Optional[int] = None,
    ):
        self.epochs = number_of_epochs

        # Number of records, determine from first not None argument.
        self.m_ = next(a.shape[0] for a in args if a is not None)
        self.mini_batch_size_: int = min(int(mini_batch_size), self.m_)

        # In principle this function can handle an arbitrarily large tuple of arrays,
        # but for simplicity, we use only the training data and the labels (if
        # specified).
        self.arrays_ = args

        # Shuffle data, if needed.
        if shuffle_data_once:
            self.shuffle()
        self.shuffle_each_epoch_ = shuffle_each_epoch

    def shuffle(self):
        """
        Shuffle internal arrays in a consistent way.
        """
        result = [None] * len(self.arrays_)
        array_indices = []
        arrays_to_shuffle = []
        # Find not None arrays that need shuffling.
        for i, array in enumerate(self.arrays_):
            if array is not None:
                array_indices.append(i)
                arrays_to_shuffle.append(array)

        # Shuffle them altogether, for index consistency.
        shuffled_arrays = shuffle(*tuple(arrays_to_shuffle))

        # `shuffle` returns matrix or tuple, depending on number of arguments.
        if isinstance(shuffled_arrays, (np.ndarray, pd.DataFrame)):
            shuffled_arrays = (shuffled_arrays,)

        # Set the not None elements with the shuffled array.
        for i, shuffled_array in zip(array_indices, shuffled_arrays):
            result[i] = shuffled_array
        self.arrays_ = tuple(result)

    def __iter__(self):
        """
        Initialise the counter.
        """
        self.a_ = 0
        self.current_epoch = 0
        return self

    def __next__(self):
        """
        Yield the next mini batch of data.
        """
        i_start = self.a_ * self.mini_batch_size_
        i_end = (self.a_ + 1) * self.mini_batch_size_

        # Stop after going through the data `epochs` times.
        if self.epochs is not None and i_start >= self.epochs * self.m_:
            raise StopIteration

        # Move the pointer back to the start of the array after reaching the end using
        # the modulo operator (i.e., periodic boundary conditions).
        i_start %= self.m_
        # Wrap when `i_end` exceeds `m_` by at least one.
        i_end = (i_end - 1) % self.m_ + 1

        self.a_ += 1

        data_batch = []
        # When the end of the array is somewhere halfway in between our batch.
        if i_end < i_start:
            for array in self.arrays_:
                if array is None:
                    data_batch.append(None)
                    continue
                # Combine the part until the end of te array, and the remainder starting
                # from the array's first element.
                if isinstance(array, pd.DataFrame):
                    wrapped_batch = pd.concat((array[i_start:], array[:i_end]))
                else:
                    wrapped_batch = np.vstack([array[i_start:], array[:i_end]])
                data_batch.append(wrapped_batch)
        else:
            for array in self.arrays_:
                if array is None:
                    data_batch.append(None)
                    continue
                # Slice off the data, for each array to return.
                data_batch.append(array[i_start:i_end])

        # We are entering a new epoch!
        if i_end == self.m_ or i_end < i_start:
            # N.B.: This is not so nice, because we already used some of the data of the
            # next epoch (namely, `array[:i_end]`) without shuffling it.
            if self.shuffle_each_epoch_:
                self.shuffle()
            self.current_epoch += 1

        if len(data_batch) == 1:
            return data_batch[0]

        return tuple(data_batch)


@njit
def generate_binary_permutations(n: int) -> Matrix:
    """
    Generate matrix with all possible permutations of `n` binary units {0, 1}.
    """
    # Dimension size of hidden unit permutations.
    d = 2 ** n
    H = zeros((d, n))

    # Go through all possible permutations.
    for l in range(d):
        for m in range(n):
            # Select m'th bit of integer l.
            c = (l >> m) & 1
            H[l, m] = c
    return H


def generate_binary_spin_permutations(n: int) -> np.ndarray:
    """
    Generate matrix with all possible permutations of `n` binary units {-1, 1}.
    """
    # Dimension size of hidden unit permutations.
    d = 2 ** n
    H = np.zeros((d, n))

    # Transform integer to binary string format.
    string_format = "{:0" + str(n) + "b}"
    # Go through all possible permutations.
    for l in range(d):
        binary_numbers = string_format.format(l)
        # Turn binary characters to {-1, 1} integers, and store this configuration.
        H[l] = np.array([2 * int(c) - 1 for c in binary_numbers])
    return H


def double_cross_validate(
    model,
    X,
    y,
    param_distributions: dict = {},
    m: int = 5,
    n: int = 5,
    scoring=None,
    refit: Union[bool, str] = True,
    n_iter: int = 50,
    n_jobs: int = -1,
    random_state: int = 1234,
) -> dict:
    """
    Perform `m`x`n` cross validation.
    """
    inner_cv = KFold(n_splits=m, shuffle=True, random_state=random_state)
    outer_cv = KFold(n_splits=n, shuffle=True, random_state=random_state + 1)

    cvsearch_kwargs = {
        "param_distributions": param_distributions,
        "cv": inner_cv,
        "n_iter": n_iter,
        "n_jobs": n_jobs,
        "scoring": scoring,
    }
    cv = RandomizedSearchCV(model, refit=refit, **cvsearch_kwargs)

    cv_kwargs = {"cv": outer_cv, "return_estimator": True, "scoring": scoring}
    return cross_validate(cv, X, y, **cv_kwargs)


def brier_loss(
    train_time: np.ndarray,
    train_event: np.ndarray,
    test_time: np.ndarray,
    test_event: np.ndarray,
    S_pred: np.ndarray,
    tau: float,
) -> float:
    """
    Calculate time-dependent Brier score.

    This is a convenience wrapper around scikit-surv `brier_score` function.
    """
    # Transform data in format compatible with Scikit-Survival's
    # `CensoringDistributionEstimator`.
    y_train = Surv.from_arrays(event=train_event.astype(bool), time=train_time)
    y_test = Surv.from_arrays(event=test_event.astype(bool), time=test_time)
    _, scores = metrics.brier_score(y_train, y_test, estimate=S_pred, times=tau)
    return scores[0]


def check_arrays(*numpy_arrays, dtype=float64) -> bool:
    """
    Verify if all numpy arrays are C style contiguous.
    """
    all_contigs = all(a.data.c_contiguous for a in numpy_arrays)
    if not all_contigs:
        raise TypeError("Not all arrays are C style contiguous.")
    all_dtype = all(a.dtype == dtype for a in numpy_arrays)
    if not all_dtype:
        raise TypeError("Not all arrays are 64 bit floating point values.")
    return True


def hash_array(X) -> int:
    """
    Make array read only and compute hash.
    """
    Xnp = X
    if isinstance(X, pd.DataFrame):
        Xnp = X.values
    Xnp.flags.writeable = False
    return hash(Xnp.tobytes())


def reset_random_state(seed):
    """
    Reset random state for both Numpy and Numba.
    """
    np.random.seed(seed)
    r = np.random.RandomState(seed)
    # Copy NumPy random state to Numba.
    ptr = _helperlib.rnd_get_np_state_ptr()
    ints, index = r.get_state()[1:3]
    _helperlib.rnd_set_state(ptr, (index, [int(x) for x in ints]))


def get_columns(X: Matrix, columns: list, dtype=None) -> Matrix:
    """
    Unpack the columns from the matrix in an Numpy/Pandas agnostic way.
    """
    if columns:
        # Unpack data frame as Numpy matrices.
        if isinstance(X, pd.DataFrame):
            return ascontiguousarray(X[columns].to_numpy(dtype=dtype))

        X_sub = X[:, columns]
        if dtype is None:
            return X_sub
        return X_sub.astype(dtype)
    return array([])
