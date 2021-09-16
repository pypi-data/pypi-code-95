from typing import Callable as _Callable

from ....tools._common import cached_property
from .trade_data_stream import TradeDataStream


class Stream:
    def __init__(
        self,
        session,
        universe,
        fields,
        api,
        extended_params,
        universe_type,
        events,
        finalized_orders,
        filters,
    ):
        self._session = session
        self._universe = universe
        self._fields = fields
        self._api = api
        self._extended_params = extended_params
        self._universe_type = universe_type
        self._events = events
        self._finalized_orders = finalized_orders
        self._filters = filters

    @cached_property
    def _stream(self):
        return TradeDataStream(
            session=self._session,
            universe=self._universe,
            fields=self._fields,
            api=self._api,
            extended_params=self._extended_params,
            universe_type=self._universe_type,
            events=self._events,
            finalized_orders=self._finalized_orders,
            filters=self._filters,
        )

    def open(self):
        return self._stream.open()

    async def open_async(self, **kwargs):
        return await self._stream.open_async(**kwargs)

    def close(self):
        return self._stream.close()

    def on_update(self, on_update: _Callable):
        """
        These notifications are emitted when fields of the requested instrument change

        Parameters
        ----------
        on_update : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        -------
        >>> import datetime
        >>> from refinitiv.data.content import trade_data_service
        >>>
        >>> def display_event(event_type, event):
        ...    current_time = datetime.datetime.now().time()
        ...    print("----------------------------------------------------------")
        ...    print(">>> {} event received at {}".format(event_type, current_time))
        ...    print(event)
        >>>
        >>> definition = trade_data_service.Definition(
        ...     universe=[],
        ...     fields=[
        ...        "OrderKey",
        ...        "OrderTime",
        ...        "RIC",
        ...        "Side",
        ...        "AveragePrice",
        ...        "OrderStatus",
        ...        "OrderQuantity",
        ...],
        ...     events=trade_data_service.Events.Full,
        ...     finalized_orders=trade_data_service.FinalizedOrders.P1D
        ...)
        >>> stream = definition.get_stream()
        >>> stream.on_update(lambda item_stream, event: display_event("Update", event))
        >>> stream.open()
        """
        self._stream._on_update_cb = on_update
        return self

    def on_complete(self, on_complete: _Callable):
        """
        Full data of requested universe items

        Parameters
        ----------
        on_complete : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        -------
        >>> import datetime
        >>> from refinitiv.data.content import trade_data_service
        >>>
        >>> def display_event(event_type, event):
        ...    current_time = datetime.datetime.now().time()
        ...    print("----------------------------------------------------------")
        ...    print(">>> {} event received at {}".format(event_type, current_time))
        ...    print(event)
        >>>
        >>> definition = trade_data_service.Definition(
        ...     universe=[],
        ...     fields=[
        ...        "OrderKey",
        ...        "OrderTime",
        ...        "RIC",
        ...        "Side",
        ...        "AveragePrice",
        ...        "OrderStatus",
        ...        "OrderQuantity",
        ...],
        ...     events=trade_data_service.Events.Full,
        ...     finalized_orders=trade_data_service.FinalizedOrders.P1D
        ...)
        >>> stream = definition.get_stream()
        >>> stream.on_complete(lambda item_stream, event: display_event("Complete", event))
        >>> stream.open()
        """
        self._stream._on_complete_cb = on_complete
        return self

    def on_add(self, on_add: _Callable):
        """
        These notifications are sent when the status of one of the requested instruments is added

        Parameters
        ----------
        on_add : Callable
            Callable object to process retrieved data

        Returns
        -------
        current instance

        Examples
        -------
        >>> import datetime
        >>> from refinitiv.data.content import trade_data_service
        >>>
        >>> def display_event(event_type, event):
        ...    current_time = datetime.datetime.now().time()
        ...    print("----------------------------------------------------------")
        ...    print(">>> {} event received at {}".format(event_type, current_time))
        ...    print(event)
        >>>
        >>> definition = trade_data_service.Definition(
        ...     universe=[],
        ...     fields=[
        ...        "OrderKey",
        ...        "OrderTime",
        ...        "RIC",
        ...        "Side",
        ...        "AveragePrice",
        ...        "OrderStatus",
        ...        "OrderQuantity",
        ...],
        ...     events=trade_data_service.Events.Full,
        ...     finalized_orders=trade_data_service.FinalizedOrders.P1D
        ...)
        >>> stream = definition.get_stream()
        >>> stream.on_add(lambda item_stream, event: display_event("Add", event))
        >>> stream.open()
        """
        self._stream._on_add_cb = on_add
        return self

    def on_remove(self, on_remove: _Callable):
        self._stream._on_remove_cb = on_remove
        return self

    def on_event(self, on_event: _Callable):
        """
        These notifications are emitted when the status of one of the requested instruments changes

        Parameters
        ----------
        on_event

        Returns
        -------
        current instance

        Examples
        -------
        >>> import datetime
        >>> from refinitiv.data.content import trade_data_service
        >>>
        >>> def display_event(event_type, event):
        ...    current_time = datetime.datetime.now().time()
        ...    print("----------------------------------------------------------")
        ...    print(">>> {} event received at {}".format(event_type, current_time))
        ...    print(event)
        >>>
        >>> definition = trade_data_service.Definition(
        ...     universe=[],
        ...     fields=[
        ...        "OrderKey",
        ...        "OrderTime",
        ...        "RIC",
        ...        "Side",
        ...        "AveragePrice",
        ...        "OrderStatus",
        ...        "OrderQuantity",
        ...],
        ...     events=trade_data_service.Events.Full,
        ...     finalized_orders=trade_data_service.FinalizedOrders.P1D
        ...)
        >>> stream = definition.get_stream()
        >>> stream.on_event(lambda item_stream, event: display_event("Event", event))
        >>> stream.open()
        """
        self._stream._on_event_cb = on_event
        return self

    def on_state(self, on_state: _Callable):
        """
        These notifications are emitted when the state of one of the requested changes

        Parameters
        ----------
        on_state : Callable

        Returns
        -------
        current instance

        Examples
        -------
        >>> import datetime
        >>> from refinitiv.data.content import trade_data_service
        >>>
        >>> def display_event(event_type, event):
        ...    current_time = datetime.datetime.now().time()
        ...    print("----------------------------------------------------------")
        ...    print(">>> {} event received at {}".format(event_type, current_time))
        ...    print(event)
        >>>
        >>> definition = trade_data_service.Definition(
        ...     universe=[],
        ...     fields=[
        ...        "OrderKey",
        ...        "OrderTime",
        ...        "RIC",
        ...        "Side",
        ...        "AveragePrice",
        ...        "OrderStatus",
        ...        "OrderQuantity",
        ...],
        ...     events=trade_data_service.Events.Full,
        ...     finalized_orders=trade_data_service.FinalizedOrders.P1D
        ...)
        >>> stream = definition.get_stream()
        >>> stream.on_state(lambda item_stream, event: display_event("State", event))
        >>> stream.open()
        """
        self._stream._on_state_cb = on_state
        return self
