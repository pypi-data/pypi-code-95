from abc        import ABCMeta, abstractmethod
from functools  import wraps
from time       import time

from .settings  import config, LogType, ReleaseType


class Profiler(metaclass=ABCMeta):
    """Base class for profilers

    To profile a program, create an instance ``p`` of one of the ``Profiler``
    implementations and apply the ``@p.profile`` decorator to all functions that
    should be investigated.

    Example::

        import plogpro
        p = plogpro.TracingProfiler("results.json")

        @p.profile
        def func()
            # do something ...
            pass

        func()

    To create a custom profiler, create a subclass of ``Profiler`` and implement
    the method ``write(self, name, start_time, end_time)`` that accepts 3
    arguments:

    * ``name``: the name of the decorated function
    * ``start_time``: the start time in seconds since Epoch
    * ``end_time``: the end time in seconds since Epoch

    If you need to do anything once in the beginning or the and, you can
    override the ``setup()`` and/or ``teardown()`` methods respectively.

    Warning:
        The ``profile()`` method should **not** be overwritten.
    """

    def __init__(self):
        if config["release"] < ReleaseType.RELEASE_QUIET:
            self.setup()

    def __del__(self):
        if config["release"] < ReleaseType.RELEASE_QUIET:
            self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass

    def profile(self, func):
        """Decorator to use for profiling a function
        """
        if config["release"] >= ReleaseType.RELEASE:
            return func

        @wraps(func)
        def profiled_func(*args, **kwargs):
            start_time = time()
            func(*args, **kwargs)
            end_time = time()
            self.write(func.__name__, start_time, end_time)
        return profiled_func

    @abstractmethod
    def write(self, name, start_time, end_time):
        raise NotImplementedError
