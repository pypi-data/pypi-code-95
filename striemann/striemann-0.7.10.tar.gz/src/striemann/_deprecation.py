import warnings
import functools


def deprecated(alternative_text=""):
    """Mark a function deprecated.

    When the function is called, a warnings framework warning will be emitted.

    alternative_text (str): What client should do instead
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                "Call to deprecated function {}. {}".format(
                    func.__name__, alternative_text
                ),
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
