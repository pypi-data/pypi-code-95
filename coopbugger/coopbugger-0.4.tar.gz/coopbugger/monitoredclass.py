import functools
import time
import logging
import inspect
import types

class MonitoredClass():
    def __init__(self):
        self.tracked_time = {}

    def timer(func):
        """Print the runtime of the decorated function"""
        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            # capture time
            start_time = time.perf_counter()  # 1
            value = func(*args, **kwargs)
            end_time = time.perf_counter()  # 2
            run_time = end_time - start_time  # 3

            # cant track on static method
            if len(args) > 0 and not isinstance(func, types.FunctionType):
                args[0].tracked_time.setdefault(func.__name__, 0)
                args[0].tracked_time[func.__name__] += run_time

            logging.debug(f"Finished {func.__name__!r} in {run_time:.4f} secs")
            return value

        return wrapper_timer


    def debug(func):
        """Print the function signature and return value"""

        @functools.wraps(func)
        def wrapper_debug(*args, **kwargs):
            args_repr = [repr(a) for a in args]  # 1
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
            signature = ", ".join(args_repr + kwargs_repr)  # 3
            logging.debug(f"Caller {inspect.stack()[1][3]} is calling {func.__name__}({signature})")
            value = func(*args, **kwargs)
            logging.debug(f"{func.__name__!r} returned {value!r}")  # 4
            return value

        return wrapper_debug

class MyClass(MonitoredClass):
    @MonitoredClass.timer
    def test(self):
        time.sleep(1)

    @MonitoredClass.debug
    def _my_called_func(self, *args):
        return sum(args)

    def my_caller_func(self):
        self._my_called_func(1, 2, 3)

    @staticmethod
    @MonitoredClass.timer
    def test_static():
        time.sleep(1)

if __name__ == "__main__":
    loggingLvl = logging.DEBUG

    rootLogger = logging.getLogger('')
    rootLogger.handlers = []
    rootLogger.setLevel(loggingLvl)

    #formatters
    # fileFormatter = logging.Formatter('%(name)s -- %(asctime)s : [%(levelname)s] %(message)s (%(filename)s lineno: %(lineno)d)')
    consoleFormatter = logging.Formatter('%(name)s -- %(asctime)s : [%(levelname)s] %(message)s (%(filename)s lineno: %(lineno)d)')
    uiFormatter = logging.Formatter(' %(levelname)s: %(message)s')


    #Console Handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(consoleFormatter)
    rootLogger.addHandler(console)

    cls = MyClass()

    for ii in range(0, 5):
        cls.test()

    cls.my_caller_func()
    cls.test_static()
    print(cls.tracked_time)
