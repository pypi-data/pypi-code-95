import abc
import enum

from eventemitter import EventEmitter

from .state import State
from .state import StreamState
from ...tools._common import cached_property


class StateEvent(enum.Enum):
    OPEN = "open"
    CLOSE = "close"


class StateManager(State, abc.ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._loop = kwargs.get("loop")
        self._next_state = None
        self._prev_state = None
        self._kwargs = None

    @cached_property
    def _emitter(self) -> EventEmitter:
        return EventEmitter(self._loop)

    def on(self, event, listener):
        return self._emitter.on(event, listener)

    @property
    def is_open(self) -> bool:
        return self.state is StreamState.Open

    @property
    def is_pause(self) -> bool:
        return self.state is StreamState.Pause

    @property
    def is_close(self) -> bool:
        return self.state is StreamState.Closed

    def open(self, **kwargs):
        return self._loop.run_until_complete(self.open_async(**kwargs))

    async def open_async(self, **kwargs):
        if self.is_open:
            return self.state

        if self.is_pause:
            self._next_state = StreamState.Open
            self._kwargs = kwargs
            return self.state

        await self._do_open_async(**kwargs)
        self.state = StreamState.Open
        self._emitter.emit(StateEvent.OPEN, self)
        return self.state

    @abc.abstractmethod
    async def _do_open_async(self, **kwargs):
        # for override
        pass

    def close(self, **kwargs):
        return self._loop.run_until_complete(self.close_async(**kwargs))

    async def close_async(self, **kwargs):
        if self.is_close:
            return self.state

        await self._do_close_async(**kwargs)
        self.state = StreamState.Closed
        self._emitter.emit(StateEvent.CLOSE, self)
        return self.state

    @abc.abstractmethod
    async def _do_close_async(self, **kwargs):
        # for override
        pass

    def pause(self):
        if self.is_pause:
            return self.state

        self._set_pause()
        self._do_pause()

        return self.state

    def _set_pause(self):
        self._prev_state = self.state
        self.state = StreamState.Pause

    @abc.abstractmethod
    def _do_pause(self):
        # for override
        pass

    def resume(self):
        if not self.is_pause:
            return self.state

        self._set_resume()

        if self._next_state is StreamState.Open:
            self.open(**self._kwargs)

        self._do_resume()

        return self.state

    def _set_resume(self):
        self.state = self._prev_state

    @abc.abstractmethod
    def _do_resume(self):
        # for override
        pass
