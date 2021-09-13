from functools import update_wrapper
from functools import wraps
from typing import Any, Callable, cast, Final, Tuple, TypeVar

from _thread import allocate_lock as _create_mutex
from _thread import LockType as _MutexType
from _thread import start_new_thread as _start_thread

__all__: Final[Tuple[str, ...]] = ("AnyFunc", "synchronized", "threaded")

AnyFunc = TypeVar("AnyFunc", bound=Callable[..., Any])


def synchronized(user_function: AnyFunc, /) -> AnyFunc:
    """
    A decorator to synchronize a ``user_function``.
    """
    mutex: _MutexType = _create_mutex()

    @wraps(user_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with mutex:
            return user_function(*args, **kwargs)

    return cast(AnyFunc, wrapper)


def threaded(user_function: AnyFunc, /) -> Callable[..., int]:
    """
    A decorator to run a ``user_function`` in a separate thread.
    """
    def callback(*args: Any, **kwargs: Any) -> None:  # pragma: no cover
        try:
            user_function(*args, **kwargs)
        finally:
            # Exit from the interpreter immediately:
            raise SystemExit from None

    run_in_thread: Callable[..., int] = lambda *args, **kwargs: _start_thread(callback, args, kwargs)
    return update_wrapper(run_in_thread, user_function)
