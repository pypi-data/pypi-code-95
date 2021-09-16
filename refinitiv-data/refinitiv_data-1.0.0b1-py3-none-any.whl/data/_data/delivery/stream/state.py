# coding: utf-8

from enum import Enum, unique

from threading import Lock


@unique
class StreamState(Enum):
    """
    Define the state of the Stream.

    Closed  :   The Stream is closed and ready to be opened.
    Open    :   The Stream is opened.
    Pause   :   The Stream is paused.
    """

    Closed = 1
    Open = 3
    Pause = 4


class State(object):
    def __init__(self, *args, **kwargs):
        self._state = StreamState.Closed
        self._state_lock = Lock()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        with self._state_lock:
            self._state = value
