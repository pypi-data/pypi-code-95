from scipy.sparse import csc_matrix, csr_matrix
from numpy import ndarray
from sys import getsizeof

__all__ = [
    'mem_usage',
]


def mem_usage(obj, human=True):
    from humanize import naturalsize
    mem = __memory_usage(obj)
    shape = __shape(obj)
    if human:
        if shape is not None:
            return '{0} \t{1}'.format(naturalsize(mem), shape)
        else:
            return '{0}'.format(naturalsize(mem))
    else:
        return mem


def __memory_usage(obj):
    if isinstance(obj, csc_matrix) or isinstance(obj, csr_matrix):
        return obj.data.nbytes + obj.indptr.nbytes + obj.indices.nbytes
    elif isinstance(obj, ndarray):
        return obj.nbytes
    else:
        return getsizeof(obj)


def __shape(obj):
    if isinstance(obj, csc_matrix) or isinstance(obj, csr_matrix) or isinstance(obj, ndarray):
        return obj.shape
    else:
        return None
