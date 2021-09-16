# coding: utf8

import re
import traceback
from typing import Callable

from .event import Event
from .eventemitter import StreamingPriceEventEmitter
from ...delivery.stream import StateEvent
from ...core import get_valid_session
from ...core.log_reporter import _LogReporter
from ...delivery.stream import OMMStream
from ...delivery.stream import StateManager
from ...delivery.stream.stream_cache import StreamCache
from ...tools._common import cached_property

# regular expression pattern for intra-field position sequence
_partial_update_intra_field_positioning_sequence_regular_expression_pattern = (
    r"[\x1b\x5b|\x9b]([0-9]+)\x60([^\x1b^\x5b|^\x9b]+)"
)
_huge = 1e12


def _decode_intra_field_position_sequence(cached_value, new_value):
    # find all partial update in the value
    tokens = re.findall(
        _partial_update_intra_field_positioning_sequence_regular_expression_pattern,
        new_value,
    )

    # check this value contains a partial update or not?
    if len(tokens) == 0:
        # no partial update required, so done
        return new_value

    # do a partial update
    updated_value = cached_value
    for (offset, replace) in tokens:
        # convert offset from str to int
        offset = int(offset)
        assert offset < len(updated_value)

        # replace the value in the string
        updated_value = (
            updated_value[:offset] + replace + updated_value[offset + len(replace) :]
        )

    # done, return
    return updated_value


class StreamingPrice(StreamCache, StateManager, _LogReporter):
    def __init__(
        self,
        name,
        session=None,
        fields=None,
        service=None,
        api=None,
        extended_params=None,
        on_refresh=None,
        on_status=None,
        on_update=None,
        on_complete=None,
        on_error=None,
    ):
        if name is None:
            raise AttributeError("Instrument name must be defined.")

        session = get_valid_session(session)

        StreamCache.__init__(self, name=name, fields=fields, service=service)
        StateManager.__init__(self, loop=session._loop, logger=session)
        _LogReporter.__init__(self, logger=session)

        self._session = session
        self._api = api
        self._extended_params = extended_params
        self._on_event(Event.REFRESH, on_refresh)
        self._on_event(Event.STATUS, on_status)
        self._on_event(Event.UPDATE, on_update)
        self._on_event(Event.COMPLETE, on_complete)
        self._on_event(Event.ERROR, on_error)
        self._emitter.on(self._emitter.LISTENER_ERROR_EVENT, self._on_listener_error)

    @cached_property
    def _stream(self) -> OMMStream:
        omm_stream = OMMStream(
            session=self._session,
            name=self._name,
            service=self._service,
            fields=self._fields,
            api=self._api,
            extended_params=self._extended_params,
            on_refresh=self._on_stream_refresh,
            on_status=self._on_stream_status,
            on_update=self._on_stream_update,
            on_complete=lambda stream: self._emitter.emit(Event.COMPLETE, self),
            on_error=lambda stream, error: self._emitter.emit(Event.ERROR, self, error),
        )
        omm_stream.on(StateEvent.CLOSE, lambda *_: self.close())
        return omm_stream

    @cached_property
    def _emitter(self) -> StreamingPriceEventEmitter:
        return StreamingPriceEventEmitter(loop=self._loop)

    @property
    def code(self):
        return self._stream._code

    @property
    def message(self):
        return self._stream._message

    def on_refresh(self, func: Callable) -> "StreamingPrice":
        return self._on_event(Event.REFRESH, func, halt_if_none=True)

    def on_update(self, func: Callable) -> "StreamingPrice":
        return self._on_event(Event.UPDATE, func, halt_if_none=True)

    def on_status(self, func: Callable) -> "StreamingPrice":
        return self._on_event(Event.STATUS, func, halt_if_none=True)

    def on_complete(self, func: Callable) -> "StreamingPrice":
        return self._on_event(Event.COMPLETE, func, halt_if_none=True)

    def on_error(self, func: Callable) -> "StreamingPrice":
        return self._on_event(Event.ERROR, func, halt_if_none=True)

    def _on_event(self, event, func, halt_if_none=False):
        if not func and halt_if_none:
            raise ValueError(f"Cannot subscribe to event {event} because no listener")

        if not func and not halt_if_none:
            return

        self._emitter.on(event, func)
        return self

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def _set_pause(self):
        # do nothing
        pass

    def _set_resume(self):
        # do nothing
        pass

    def _do_pause(self):
        self._stream.pause()

    def _do_resume(self):
        self._stream.resume()

    async def _do_close_async(self):
        id_ = self._stream.stream_id
        self._debug(f"Stop StreamingPrice subscription {id_} to {self._name}")
        await self._stream.close_async()

    async def _do_open_async(self, with_updates=True):
        id_ = self._stream.stream_id
        self._debug(f"Open async StreamingPrice {id_} to {self._name}")
        await self._stream.open_async(with_updates=with_updates)

    def _decode_partial_update_field(self, key, value):
        """
        This legacy is used to process the partial update
        RETURNS the processed partial update data
        """

        fields = self._record.get("Fields")
        if key not in fields:
            fields[key] = value
            self._warning(f"key {key} not in self._record['Fields']")
            return value

        # process infra-field positioning sequence
        cached_value = fields[key]
        updated_value = _decode_intra_field_position_sequence(cached_value, value)

        # done
        return updated_value

    def _write_to_record(self, message):
        for data in message:
            if data == "Fields":
                # fields data
                # loop over all update items
                for key, value in message[data].items():
                    # only string value need to check for a partial update
                    if isinstance(value, str):
                        # value is a string, so check for partial update string
                        # process partial update and update the callback
                        # with processed partial update
                        message[data][key] = self._decode_partial_update_field(
                            key, value
                        )

                # update the field data
                self._record[data].update(message[data])
            else:
                # not a "Fields" data
                self._record[data] = message[data]

    def _on_stream_refresh(self, stream, message):
        self._record = message
        fields = message.get("Fields")
        self._emitter.emit(Event.REFRESH, self, fields)

    def _on_stream_status(self, stream, status):
        self._status = status
        self._emitter.emit(Event.STATUS, self, status)

    def _on_stream_update(self, stream, update):
        self._write_to_record(update)
        fields = update.get("Fields")
        self._emitter.emit(Event.UPDATE, self, fields)

    def _on_listener_error(self, event, listener, exc):
        self._error(f"StreamingPrice on_{event} callback raised exception: {exc!r}")
        self._debug(f"{traceback.format_exc()}")
