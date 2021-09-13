import time
import datetime
from functools import wraps

"""
:authors: n.lebedevvv
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2021 n.lebedevvv
"""


def timer(function):
    """
    Execution time counting decorator
    Print the result to the console.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = round(datetime.datetime.utcnow().timestamp() * 1000)
        result = function(*args, **kwargs)
        end = round(datetime.datetime.utcnow().timestamp() * 1000)

        execution_time = (end - start) / 1000

        print(f'[*] Execution time: {execution_time} sec')
        return result

    return wrapper


def naked_timer(function):
    """
    Execution time counting decorator.
    :returns: dictionary | {'execution time': float, 'result': any}
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = round(datetime.datetime.utcnow().timestamp() * 1000)
        result = function(*args, **kwargs)
        end = round(datetime.datetime.utcnow().timestamp() * 1000)

        execution_time = (end - start) / 1000

        return {
            'execution_time': execution_time,
            'result': result
        }

    return wrapper


def pause(seconds: int or float):
    """
    Pause-creating decorator.
    @pause(seconds: int or float)
    """
    def wrapper(function):

        @wraps(function)
        def wrap(*args, **kwargs):
            time.sleep(seconds)
            return function(*args, **kwargs)

        return wrap

    return wrapper


def counter(function):
    """
    Decorator counting the count of calls function
    Print the result to the console.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        result = function(*args, **kwargs)
        print(f'[*] Function [{function.__name__}] was called: {wrapper.count}x')
        return result

    wrapper.count = 0

    return wrapper


def logging(function):
    """
    Logging decorator.
    (Just print information about the called function. Real logging will be added later).
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        print(f'[*] Function: {function.__name__} \n (*) args: {args} \n (*) kwargs: {kwargs}')
        return result

    return wrapper