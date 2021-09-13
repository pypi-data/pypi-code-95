from functools import partial
from multiprocessing import cpu_count
from typing import Callable, Optional

from pathos.multiprocessing import ProcessingPool as Pool

from parallely.base import ParalellyFunction
from parallely.utils import prepare_arguments


class ParallelFunction(ParalellyFunction):
    def _execute_once(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def _serial_func(self, arg_list, kwarg_list):
        return [self._func(*args, **kwargs) for args, kwargs in zip(arg_list, kwarg_list)]

    def _chunks(self, elements, n):
        def chunker(elements, n):
            steps = len(elements) // n
            for i, index in enumerate(range(0, len(elements), steps)):
                yield elements[index : index + steps] if i != n else elements[index:]

        return list(chunker(elements, n))

    def map(self, *args, **kwargs):
        args, kwargs = prepare_arguments(args, kwargs)
        pool_size = min(self._max_workers, len(args))

        with Pool(pool_size) as pool:
            results = []

            arg_chunks = self._chunks(args, pool_size)
            kwarg_chunks = self._chunks(kwargs, pool_size)
            for chunk in pool.map(self._serial_func, arg_chunks, kwarg_chunks):
                results += chunk

        return results


def parallel(func: Callable = None, max_workers: Optional[int] = None) -> ParallelFunction:
    """

    :param func:
    :param max_workers:
    :return:
    """
    max_workers = max_workers if max_workers is not None else cpu_count()

    if func is None:
        return partial(parallel, max_workers=max_workers)

    return ParallelFunction(func, max_workers)
