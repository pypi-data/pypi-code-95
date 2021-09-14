# -*- coding: utf-8 -*-

"""Main module."""

import asyncio
from contextlib import contextmanager
from typing import Optional

__author__ = """Eugene M. Kim"""
__email__ = 'astralblue@gmail.com'
__version__ = '0.3.0'


class TimeMachine:
    """A monkey-patch helper to advance an event loop's time.

    :param event_loop: the event loop to monkey-patch (default: main loop).
    """

    def __init__(self, *poargs,
                 event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 **kwargs):
        """Initialize this instance."""
        super().__init__(*poargs, **kwargs)
        if event_loop is None:
            event_loop = asyncio.get_event_loop()
        self.__loop = event_loop
        self.__original_time = event_loop.time
        self.__delta = 0
        self.__loop.time = self.__time

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__loop.time = self.__original_time

    def __time(self):
        return self.__original_time() + self.__delta

    def advance_by(self, amount: float):
        """Advance the time reference by the given amount.

        :param amount: number of seconds to advance.
        :raise `ValueError`: if *amount* is negative.
        """
        if amount < 0:
            raise ValueError("cannot retreat time reference: amount {} < 0"
                             .format(amount))
        self.__delta += amount

    def advance_to(self, timestamp: float):
        """Advance the time reference so that now is the given timestamp.

        :param timestamp: the new current timestamp.
        :raise `ValueError`: if *timestamp* is in the past.
        """
        now = self.__original_time()
        if timestamp < now:
            raise ValueError("cannot retreat time reference: "
                             "target {} < now {}"
                             .format(timestamp, now))
        self.__delta = timestamp - now
