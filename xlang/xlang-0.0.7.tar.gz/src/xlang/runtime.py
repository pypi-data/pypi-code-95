import time
from contextlib import contextmanager

from functools import wraps


@contextmanager
def timeblock(label):
    start = time.process_time()
    try:
        yield
    finally:
        end = time.process_time()
        print(f'{label} : {(end - start):.2f}')


def timefunc(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.process_time()
        r = func(*args, **kwargs)
        end = time.process_time()
        print(f'{func.__module__}.{func.__name__} : {(end - start):.2f}')
        return r

    return wrapper
