import abc
import inspect
import functools
from .registry import registry
from .enums import Hook


class AbstractHook(object, metaclass=abc.ABCMeta):

    __hook__: Hook = None  # type: ignore

    def __init__(self, registry=registry):
        self._registry = registry

    def __call__(self, func, *args, **kwargs):

        @functools.wrap
        def wrapped(*args, **kwargs):
            func(*args, **kwargs)

        self._registry.add_hook(self.__hook__, func)
        return wrapped


class pre_step(AbstractHook):  # noqa

    __name__ = "pre_step"
    __hook__ = Hook.pre_step


class post_step(AbstractHook):  # noqa

    __name__ = "post_step"
    __hook__ = Hook.post_step


def register_type(func):

    @functools.wrap
    def wrapped(*args, **kwargs):
        func(*args, **kwargs)

    sig = inspect.signature(func)
    registry.add_type(sig.return_annotation, func)
    return wrapped
