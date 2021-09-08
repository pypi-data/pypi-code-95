"""
Utility tools for timout handling
"""
import functools
import errno
import os
import signal
import typing

import w7x


def timeout(
    seconds: typing.Union[int, float] = None,
    max_calls: int = 1,
    default: typing.Callable = None,
    error_message=os.strerror(errno.ETIME),
):
    """
    Decorator that raises TimeoutError if given time is exceeded.

    Args:
        seconds(int): time to wait until triggering the exception
        error_message(str)

    Examples:
        >>> import time
        >>> import w7x

        >>> def long_runtime():
        ...     time.sleep(2)
        ...     print("Done")

        >>> initial_distribute_state = w7x.distribute.ENABLED

        No timeout
        >>> w7x.distribute.disable()
        >>> _ = w7x.lib.timeout.timeout(None)(long_runtime)()
        Done

        Timeout a long running function with the expiry of 1 second. (only works outside threading)
        >>> with w7x.distribute(False):
        ...     _ = w7x.lib.timeout.timeout(1)(long_runtime)()  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TimeoutError: Timer expired

        With threading enabled timeout is not active.
        >>> w7x.distribute.enable()
        >>> _ = w7x.lib.timeout.timeout(1)(long_runtime)()
        Done

        >>> def default():
        ...     print("Default")

        Provide a default function to call in case of timeout
        >>> with w7x.distribute(False):
        ...     _ = w7x.lib.timeout.timeout(1, default=default)(long_runtime)()
        Default

        Set back distribute to initial state
        >>> w7x.distribute.ENABLED = initial_distribute_state

    """
    if seconds is None:
        seconds = 0

    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if os.name == "nt" or w7x.distribute.enabled():
                # signal.SIGALRM not existing under windows :/ and with threading
                result = func(*args, **kwargs)
            else:
                for i in range(max_calls):
                    try:
                        signal.signal(signal.SIGALRM, _handle_timeout)
                        signal.setitimer(signal.ITIMER_REAL, seconds)
                    except ValueError as err:
                        if (
                            str(err)
                            == "signal only works in main thread of the main interpreter"
                        ):
                            pass
                        else:
                            raise err
                    try:
                        result = func(*args, **kwargs)
                    except TimeoutError as err:
                        if i == max_calls - 1:
                            if default is None:
                                raise TimeoutError(error_message) from err
                            result = default()
                    else:
                        break
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
            return result

        return wrapper

    return decorator
