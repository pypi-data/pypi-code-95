from pathos.multiprocessing import ProcessingPool as Pool
from functools import partial
from multiprocessing import cpu_count

from parallely.base import ParalellyFunction
from parallely.utils import prepare_arguments


class ParallelFunction(ParalellyFunction):

    def _execute_once(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def _serial_func(self, arg_list, kwarg_list):
        return [self._func(*args, **kwargs) for args, kwargs in zip(arg_list, kwarg_list)]

    def _chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        """
        l = list(l)
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def map(self, *args, **kwargs):
        args, kwargs = prepare_arguments(args, kwargs)
        pool_size = min(self._max_workers, len(args))

        with Pool(pool_size) as pool:
            results = []
            for chunk in pool.map(self._serial_func, self._chunks(args, pool_size), self._chunks(kwargs, pool_size)):
                results += chunk

        return results


def parallel(func=None, max_workers=cpu_count()):
    if func is None:
        return partial(parallel, max_workers=max_workers)

    return ParallelFunction(func, max_workers)
