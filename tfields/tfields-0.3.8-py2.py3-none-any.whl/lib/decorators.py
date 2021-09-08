"""
Function decoration
"""
import time
import functools


class cached_property(object):  # pylint: disable=invalid-name
    """Decorator for read-only properties evaluated only once within TTL period.

    It can be used to create a cached property like this::

        import random

        # the class containing the property must be a new-style class
        class MyClass(object):
            # create property whose value is cached for ten minutes
            @cached_property(ttl=600)
            def randint(self):
                # will only be evaluated every 10 min. at maximum.
                return random.randint(0, 100)

    The value is cached  in the '_cache' attribute of the object instance that
    has the property getter method wrapped by this decorator. The '_cache'
    attribute value is a dictionary which has a key for every property of the
    object which is wrapped by this decorator. Each entry in the cache is
    created only when the property is accessed for the first time and is a
    two-element tuple with the last computed property value and the last time
    it was updated in seconds since the epoch.

    The default time-to-live (TTL) is zero seconds. Set the TTL to
    zero for the cached value to never expire.

    To expire a cached property value manually just do::

        del instance._cache[<property name>]

    """

    def __init__(self, ttl=0):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError, TypeError):
            # no cache entry found
            value = self.fget(inst)
            try:
                if inst._cache is None:
                    raise AttributeError
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value


def parametrized(dec):
    """
    possibility to parametrize a decorator
    """

    def layer(*args, **kwargs):
        def repl(fun):
            return dec(fun, *args, **kwargs)

        return repl

    return layer


@parametrized
def once(method, arg=False):
    """
    Decorator for running a method only once
    Examples:
        >>> from tfields.lib.decorators import once
        >>> class A(object):
        ...     def __init__(self):
        ...         self._once_switch = False
        ...     @property
        ...     def once_switch(self):
        ...         return self._once_switch
        ...     @once_switch.setter
        ...     def once_switch(self, value):
        ...         self._once_switch = value
        ...     @once('once_switch')
        ...     def foo(self):
        ...             return True
        >>> a = A()
        >>> assert a.once_switch == False
        >>> assert a.foo() == True
        >>> assert a.once_switch == True

    Raises:
        >>> assert a.foo()  # doctest: +ELLIPSIS
        Traceback (most recent call last):
          ...
        RuntimeError: Argument once_switch indicates the method has been run
            already

    """

    @functools.wraps(method)
    def decorator(self, *args, **kwargs):
        if getattr(self, arg):
            raise RuntimeError(
                "Argument {arg} indicates the method has been "
                "run already".format(**locals())
            )
        value = method(self, *args, **kwargs)
        setattr(self, arg, True)
        return value

    return decorator


if __name__ == "__main__":
    import doctest

    doctest.testmod()
