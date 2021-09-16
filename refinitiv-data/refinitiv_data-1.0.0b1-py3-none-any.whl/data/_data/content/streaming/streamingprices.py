# coding: utf8

import asyncio
import traceback
from typing import Union, Callable

from pandas import DataFrame

from .event import Event
from .eventemitter import StreamingPriceEventEmitter
from .streamingprice import StreamingPrice
from ... import (
    Session,
    StreamingPricesError,
)
from ...core import get_valid_session
from ...core.log_reporter import _LogReporter
from ...delivery.stream.state import StreamState
from ...delivery.stream.state_manager import StateManager, StateEvent
from ...tools._common import universe_arg_parser, fields_arg_parser, cached_property


class StreamingPrices(StateManager, _LogReporter):
    def __init__(
        self,
        universe: Union[str, list],
        session: Session = None,
        fields: Union[str, list] = None,
        service: str = None,
        api: str = None,
        on_refresh: Callable = None,
        on_status: Callable = None,
        on_update: Callable = None,
        on_complete: Callable = None,
        extended_params: dict = None,
    ) -> None:
        session = get_valid_session(session)

        StateManager.__init__(self, loop=session._loop, logger=session)
        _LogReporter.__init__(self, logger=session)

        self.universe = universe_arg_parser.get_list(universe)
        self._session = session
        self.fields = fields_arg_parser.get_list(fields or [])
        self._service = service
        self._api = api

        self._on_event(Event.REFRESH, on_refresh)
        self._on_event(Event.STATUS, on_status)
        self._on_event(Event.UPDATE, on_update)
        self._on_event(Event.COMPLETE, on_complete)
        self._emitter.on(self._emitter.LISTENER_ERROR_EVENT, self._on_listener_error)

        self._extended_params = extended_params

        self._state = StreamState.Closed
        self._completed = set()

    @cached_property
    def _streaming_prices_by_name(self) -> dict:
        retval = {}
        for name in self.universe:
            streaming_price = StreamingPrice(
                session=self._session,
                name=name,
                fields=self.fields,
                service=self._service,
                api=self._api,
                on_refresh=lambda owner, fields: self._emitter.emit(
                    Event.REFRESH, self, owner.name, fields
                ),
                on_status=self._on_streaming_price_status,
                on_update=lambda owner, fields: self._emitter.emit(
                    Event.UPDATE, self, owner.name, fields
                ),
                on_complete=self._on_streaming_price_complete,
                on_error=lambda owner, error: self._emitter.emit(
                    Event.ERROR, self, owner.name, error
                ),
                extended_params=self._extended_params,
            )
            streaming_price.on(StateEvent.CLOSE, self._on_streaming_price_close)
            retval[name] = streaming_price
        return retval

    @cached_property
    def _emitter(self) -> StreamingPriceEventEmitter:
        return StreamingPriceEventEmitter(loop=self._loop)

    def on_refresh(self, func: Callable) -> "StreamingPrices":
        return self._on_event(Event.REFRESH, func, halt_if_none=True)

    def on_update(self, func: Callable) -> "StreamingPrices":
        return self._on_event(Event.UPDATE, func, halt_if_none=True)

    def on_status(self, func: Callable) -> "StreamingPrices":
        return self._on_event(Event.STATUS, func, halt_if_none=True)

    def on_complete(self, func: Callable) -> "StreamingPrices":
        return self._on_event(Event.COMPLETE, func, halt_if_none=True)

    def on_error(self, func: Callable) -> "StreamingPrices":
        return self._on_event(Event.ERROR, func, halt_if_none=True)

    def _on_event(self, event, func, halt_if_none=False):
        if not func and halt_if_none:
            raise ValueError(f"Cannot subscribe to event {event} because no listener")

        if not func and not halt_if_none:
            return

        self._emitter.on(event, func)
        return self

    def keys(self):
        return self._streaming_prices_by_name.keys()

    def values(self):
        return self._streaming_prices_by_name.values()

    def items(self):
        return self._streaming_prices_by_name.items()

    def __iter__(self):
        return StreamingPricesIterator(self)

    def __getitem__(self, name):
        streaming_price = self._streaming_prices_by_name.get(name, {})

        if streaming_price == {}:
            self._warning(f"'{name}' not in StreamingPrices universe")

        return streaming_price

    def __len__(self):
        return len(self._streaming_prices_by_name)

    def get_snapshot(self, universe=None, fields=None, convert=True) -> DataFrame:
        """
        Returns a Dataframe filled with snapshot values
        for a list of instrument names and a list of fields.

        Parameters
        ----------
        universe: list of strings
            List of instruments to request snapshot data on.

        fields: list of strings
            List of fields to request.

        convert: boolean
            If True, force numeric conversion for all values.

        Returns
        -------
            pandas.DataFrame

            pandas.DataFrame content:
                - columns : instrument and field names
                - rows : instrument name and field values

        Raises
        ------
            Exception
                If request fails or if server returns an error

            ValueError
                If a parameter type or value is wrong

        """

        if universe:
            for name in universe:
                if name not in self.universe:
                    raise StreamingPricesError(
                        -1,
                        f"Instrument {name} was not requested : {self.universe}",
                    )
        else:
            universe = self.universe

        if fields:
            for field in fields:
                if field not in self.fields:
                    raise StreamingPricesError(
                        -1, f"Field {field} was not requested : {self.fields}"
                    )

        _all_fields_value = {
            name: self._streaming_prices_by_name[name].get_fields(fields)
            for name in universe
        }
        _fields = []

        if not fields:
            for field_values in _all_fields_value.values():
                if field_values:
                    _fields.extend(
                        field for field in field_values.keys() if field not in _fields
                    )
        else:
            _fields = fields

        _df_source = {
            f: [_all_fields_value[name].get(f, None) for name in universe]
            for f in _fields
        }
        _price_dataframe = DataFrame(_df_source, columns=_fields)

        if convert and not _price_dataframe.empty:
            _price_dataframe = _price_dataframe.convert_dtypes()

        _price_dataframe.insert(0, "Instrument", universe)

        return _price_dataframe

    def _do_pause(self) -> None:
        for streaming_price in self.values():
            streaming_price.pause()

    def _do_resume(self) -> None:
        for streaming_price in self.values():
            streaming_price.resume()

    async def _do_open_async(self, with_updates=True) -> None:
        self._debug(f"StreamingPrices : open streaming on {self.universe}")
        self._completed.clear()
        streaming_prices_iterator = iter(self.values())

        try:
            stream_opens_socket = next(streaming_prices_iterator)
        except StopIteration:
            raise ValueError("No instrument to subscribe")

        await stream_opens_socket.open_async(with_updates=with_updates)
        await asyncio.gather(
            *[
                item.open_async(with_updates=with_updates)
                for item in streaming_prices_iterator
            ]
        )
        self._debug(f"StreamingPrices : streaming on {self.universe} is open")

    async def _do_close_async(self) -> None:
        self._debug(f"StreamingPrices : close streaming on {str(self.universe)}")
        for streaming_price in self.values():
            streaming_price.close()

    def _on_streaming_price_close(self, streaming_price):
        all_closed = all(streaming_price.is_close for streaming_price in self.values())
        if all_closed:
            self.close()

    def _on_streaming_price_status(self, streaming_price, status):
        self._emitter.emit(Event.STATUS, self, streaming_price.name, status)

        if streaming_price.is_close:
            self._on_streaming_price_complete(streaming_price)

    def _on_streaming_price_complete(self, streaming_price):
        name = streaming_price.name
        if name in self._completed:
            return

        self._completed.update([name])
        if self._completed == set(self.universe):
            self._emitter.emit(Event.COMPLETE, self)

    def _on_listener_error(self, event, listener, exc) -> None:
        self._error(f"StreamingPrices on_{event} callback raised exception: {exc!r}")
        self._debug(f"{traceback.format_exc()}")


class StreamingPricesIterator:
    def __init__(self, streaming_prices: StreamingPrices):
        self._streaming_prices = streaming_prices
        self._index = 0

    def __next__(self):
        if self._index < len(self._streaming_prices.universe):
            result = self._streaming_prices[
                self._streaming_prices.universe[self._index]
            ]
            self._index += 1
            return result
        raise StopIteration()
