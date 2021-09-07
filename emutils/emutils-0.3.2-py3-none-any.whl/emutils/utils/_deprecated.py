from typing import Union
from ..parallel.utils import nb_splits, split_indexes, split
from ..parallel import batch_process as batch_process_

from ._ipy import import_tqdm

__all__ = [
    'nb_batches',
    'batch_indexes',
    'batch_iterable',
    'batch_process',
    'batch_parallel_process',
]


def nb_batches(iterable, batch_size):
    return nb_splits(iterable, batch_size)


def batch_indexes(iterable, batch_size, **kwargs):
    return split_indexes(iterable, batch_size)


def batch_iterable(iterable, batch_size):
    return split(iterable, batch_size)


def batch_process(f, dataset, batch_size, use_tqdm='Batches', **kwargs):
    return batch_process_(f=f, iterable=dataset, split_size=batch_size, desc=use_tqdm)


def batch_parallel_process(f, iterable, batch_size, n_jobs=4, use_tqdm: Union[None, str, bool] = 'Batches', **kwargs):
    from joblib import Parallel, delayed
    tqdm = import_tqdm()

    # Compute inputs
    if n_jobs > 1 and len(iterable) > batch_size:
        iters = batch_iterable(iterable, batch_size, **kwargs)
    else:
        iters = iterable
    # Apply TQDM
    if use_tqdm is not None and use_tqdm is not False:
        iters = tqdm(iters, desc=str(use_tqdm))
    # Do the computation
    if n_jobs > 1 and len(iterable) > batch_size:
        results = Parallel(n_jobs=n_jobs)(delayed(f)(argument) for argument in iters)
        return sum(results, [])
    else:
        return f(iters)