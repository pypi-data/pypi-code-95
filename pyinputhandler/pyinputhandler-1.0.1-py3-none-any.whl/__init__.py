import threading

from .getch import getch
from .buffer_input import buffer_input
from .input_types import try_input, safe_input, safe_try_input
from . import input_types


def get_input_buffer():
    return buffer_input.get_input_buffer()


def get_safe_buffer():
    return safe_input.get_input_buffer()


def set_lock(lock):
    if not isinstance(lock, threading.Lock):
        raise TypeError("lock must be a threading.Lock instance")

    safe_input._input_lock = lock
    safe_try_input._input_lock = lock
    input_types.ThreadSafeInput._input_lock = lock
    input_types.ThreadSafeTryInput._input_lock = lock
