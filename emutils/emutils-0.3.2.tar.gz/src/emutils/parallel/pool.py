import multiprocessing
from typing import Union

import pandas as pd
import numpy as np

from tqdm import tqdm

from .utils import split, join, Element, max_cpu_count

__all__ = ['parallel_pool']


def parallel_pool(
    iterable: Element,
    func,
    n_jobs: Union[None, int] = None,
    split_size: Union[None, int] = None,
    use_tqdm: Union[None, bool, str] = True
) -> Element:
    # Defaults
    n_jobs = n_jobs or max_cpu_count()  # Default number of cores
    split_size = split_size or int(np.ceil((len(iterable) / n_jobs)))
    if use_tqdm is not None:
        if isinstance(use_tqdm, bool):
            if use_tqdm:
                use_tqdm = ''
            else:
                use_tqdm = None
    # Split
    splits = split(iterable, split_size)
    # Start pool
    n_jobs = min(n_jobs, len(splits))  # Reduce n_jobs if there are less splits
    assert n_jobs >= 1, "No inputs or n_jobs < 1."
    if n_jobs > 1:
        pool = multiprocessing.Pool(n_jobs)
        # Apply
        if n_jobs > 1:
            if use_tqdm is not None:
                use_tqdm += f' ({n_jobs} processes, {len(splits[0])} it/batch)'
                ret = join(tqdm(pool.imap(func, splits), total=len(splits), desc=use_tqdm))
            else:
                ret = join(pool.imap(func, splits))
        # Close parallelism
        pool.close()
        pool.join()
        # Return
        return ret

    else:
        # Non-parallel
        if use_tqdm is not None:
            use_tqdm += f' (single-core), {len(splits[0])} it/batch)'
            return join([func(split) for split in tqdm(splits, desc=use_tqdm, total=len(splits))])
        else:
            return join([func(split) for split in splits])