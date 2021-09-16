# coding: utf8


import logging
import traceback
from threading import Lock
from typing import Callable

from ._omm_stream import _OMMStream
from .omm_stream_callback import OMMStreamCallback
from .state import StreamState


class OMMStream(_OMMStream):
    """
    Open an OMM stream.

    Parameters
    ----------
    name: string
        RIC to retrieve item stream.

    domain: string
        Specify item stream domain (MarketPrice, MarketByPrice, ...)
        Default : "MarketPrice"

    api: string, optional
        specific name of RDP streaming defined in config file. i.e. 'streaming/trading-analytics/redi'
        Default: 'streaming/pricing/main'

    service: string, optional
        Specify the service to subscribe on.
        Default: None

    fields: string or list, optional
        Specify the fields to retrieve.
        Default: None

    extended_params: dict, optional
        Specify optional params
        Default: None

    on_refresh: callable object, optional
        Called when the stream is opened or when the record is refreshed with a new image.
        This callback receives a full image
        Default: None

    on_update: callable object, optional
        Called when an update is received.
        This callback receives an utf-8 string as argument.
        Default: None

    on_error: callable object, optional
        Called when an error occurs.
        This callback receives Exception as argument
        Default: None

    on_complete: callable object, optional
        Called when item stream received all fields.
        This callback has no argument.
        Default: None

    Raises
    ------
    Exception
        If request fails or if Refinitiv Services return an error

    Examples
    --------
    >>> import refinitiv.data as rd
    >>>
    >>> session = rd.session.desktop.Definition(app_key=APP_KEY).get_session()
    >>> session.open()
    >>>
    >>> euro = rd.delivery.omm_stream.Definition("EUR=").get_stream(session)
    >>> euro.open()
    >>>
    >>> def on_update(stream, msg):
            print(msg)
    >>>
    >>> thb = rd.delivery.omm_stream.Definition("THB=").get_stream(session).on_update(on_update)
    >>> thb.open()
    """

    class Params(object):
        def __init__(self, *args, **kwargs):
            self._name = None
            self._session = None
            self._api = None
            self._domain = "MarketPrice"
            self._service = None
            self._fields = None
            self._extended_params = None
            self._on_refresh_cb = None
            self._on_status_cb = None
            self._on_update_cb = None
            self._on_error_cb = None
            self._on_complete_cb = None

            if len(args) > 0 and isinstance(args[0], OMMStream.Params):
                self.__init_from_params__(args[0])

            if kwargs:
                self._name = kwargs.get("name")
                self._session = kwargs.get("session")
                self._api = kwargs.get("api")
                self._domain = kwargs.get("domain", "MarketPrice")
                self._service = kwargs.get("service")
                self._fields = kwargs.get("fields")
                self._extended_params = kwargs.get("extended_params", None)
                self._on_refresh_cb = kwargs.get("on_refresh")
                self._on_status_cb = kwargs.get("on_status")
                self._on_update_cb = kwargs.get("on_update")
                self._on_error_cb = kwargs.get("on_error")
                self._on_complete_cb = kwargs.get("on_complete")

        def __init_from_params__(self, params):
            self._name = getattr(params, "name", None)
            self._session = getattr(params, "session", None)
            self._api = getattr(params, "api", None)
            self._domain = getattr(params, "domain", "MarketPrice")
            self._service = getattr(params, "service", "IDN_RDF")
            self._fields = getattr(params, "fields", [])
            self._extended_params = getattr(params, "extended_params", None)
            self._on_refresh_cb = getattr(params, "on_refresh", None)
            self._on_status_cb = getattr(params, "on_status", None)
            self._on_update_cb = getattr(params, "on_update", None)
            self._on_error_cb = getattr(params, "on_error", None)
            self._on_complete_cb = getattr(params, "on_complete", None)

        def name(self, name):
            self._name = name
            return self

        def session(self, session):
            if session is None:
                raise AttributeError("Session is mandatory")
            else:
                self._session = session
            return self

        def with_api(self, api):
            if api is None:
                self._api = "streaming/pricing/main"
            else:
                self._api = api
            return self

        def with_domain(self, domain):
            if domain is None:
                self._domain = "MarketPrice"
            else:
                self._domain = domain
            return self

        def with_fields(self, fields):
            from ...legacy.tools import build_list

            if fields:
                self._fields = build_list(fields, "fields")
            else:
                self._fields = None
            return self

        def with_service(self, service):
            if service:
                self._service = service
            return self

        def with_extended_params(self, extended_params):
            self._extended_params = extended_params
            return self

        def on_status(self, on_status):
            self._on_status_cb = on_status
            return self

        def on_refresh(self, on_refresh):
            self._on_refresh_cb = on_refresh
            return self

        def on_update(self, on_update):
            self._on_update_cb = on_update
            return self

        def on_error(self, on_error):
            self._on_error_cb = on_error
            return self

        def on_complete(self, on_complete):
            self._on_complete_cb = on_complete
            return self

    def __init__(
        self,
        session,
        name,
        api=None,
        domain="MarketPrice",
        service=None,
        fields=None,
        extended_params=None,
        on_refresh=None,
        on_status=None,
        on_update=None,
        on_error=None,
        on_complete=None,
    ):
        from ...core.session import get_default

        if not session:
            session = get_default()

        if session is None:
            raise AttributeError("Session must be started")

        _OMMStream.__init__(self, session, api=api)

        self.__item_stream_lock = Lock()
        self._callbacks = OMMStreamCallback()
        self._callbacks.on_refresh = None
        self._callbacks.on_status = None
        self._callbacks.on_update = None
        self._callbacks.on_error = None
        self._callbacks.on_complete = None
        self._message = None
        self._code = None

        self.__init_from_args__(
            name=name,
            session=session,
            domain=domain,
            service=service,
            fields=fields,
            extended_params=extended_params,
            on_refresh=on_refresh,
            on_status=on_status,
            on_update=on_update,
            on_error=on_error,
            on_complete=on_complete,
        )
        if self._session is None:
            raise AttributeError("Session must be defined")
        if self._name is None:
            raise AttributeError("name must be defined.")
        if type(self._name) is list:
            raise ValueError("name can't be a list.")
        if self._fields is None:
            self._fields = []

    def __init_from_args__(
        self,
        session,
        name,
        domain,
        service,
        fields,
        extended_params,
        on_refresh,
        on_status,
        on_update,
        on_error,
        on_complete,
    ):
        self._name = name
        self._domain = domain
        self._service = service
        self._fields = fields
        self._extended_params = extended_params
        self._callbacks.on_refresh = on_refresh
        self._callbacks.on_status = on_status
        self._callbacks.on_update = on_update
        self._callbacks.on_error = on_error
        self._callbacks.on_complete = on_complete

    @property
    def status(self):
        _st = dict(
            [("status", self.state), ("code", self._code), ("message", self._message)]
        )
        return _st

    #######################################
    #  methods to open and close session  #
    #######################################
    def open(self, with_updates: bool = True) -> StreamState:
        """
        Opens the OMMStream to start to stream. Once it's opened, it can be used in order to retrieve data.

        Parameters
        ----------
        with_updates : bool, optional
            actions:
                True - the streaming will work as usual and the data will be received continuously.
                False - only one data snapshot will be received (single Refresh 'NonStreaming') and stream will be closed automatically.

            Defaults to True

        Returns
        -------
        StreamState
            current state of this OMM stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import omm_stream
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.open()
        """
        return _OMMStream.open(self, with_updates=with_updates)

    async def open_async(self, with_updates: bool = True) -> StreamState:
        """
        Opens asynchronously the OMMStream to start to stream

        Parameters
        ----------
        with_updates : bool, optional
            actions:
                True - the streaming will work as usual and the data will be received continuously.
                False - only one data snapshot will be received (single Refresh 'NonStreaming') and stream will be closed automatically.

        Returns
        -------
        StreamState
            current state of this OMM stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import omm_stream
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> await stream.open_async()
        """
        return await _OMMStream.open_async(self, with_updates=with_updates)

    def close(self) -> StreamState:
        """
        Closes the OMMStream connection, releases resources

        Returns
        -------
        StreamState
            current state of this OMM stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import omm_stream
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.open()
        >>> stream.close()
        """
        if self._session:
            self._session.debug(f"Close OMMStream subscription {self.stream_id}")

        state = super(OMMStream, self).close()
        self._code = "Closed"
        self._message = ""
        return state

    ################################################
    #  methods to open asynchronously item stream  #
    ################################################
    async def _do_open_async(self, with_updates=True):
        """
        Open the data stream
        """
        self._session.debug(
            f"Open asynchronously OMMStream {self.stream_id} to {self._name}"
        )
        if self._name is None:
            raise AttributeError("name parameter is mandatory")

        return await super()._do_open_async(with_updates=with_updates)

    #############################
    # OMMStream properties      #
    #############################

    def on_refresh(self, func: Callable):
        """
        This function called when the stream is opened or when the record is refreshed with a new image.
        This callback receives a full image.

        Parameters
        ----------
        func : Callable, optional
             Callable object to process retrieved refresh data

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_refresh(lambda stream, event: display_response(stream, 'refresh', event))
        >>>
        >>> stream.open()
        """
        self._callbacks.on_refresh = func
        return self

    def on_update(self, func: Callable):
        """
        This function called when an update is received.

        Parameters
        ----------
        func : Callable, optional
            Callable object to process retrieved update data

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_update(lambda stream, event: display_response(stream, 'update', event))
        >>>
        >>> stream.open()
        """
        self._callbacks.on_update = func
        return self

    def on_status(self, func: Callable):
        """
        This function these notifications are emitted when the status of one of the requested instruments changes

        Parameters
        ----------
        func : Callable, optional
            Callable object to process retrieved status data

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_status(lambda stream, event: display_response(stream, 'status', event))
        >>>
        >>> stream.open()
        """
        self._callbacks.on_status = func
        return self

    def on_error(self, func: Callable):
        """
        This function called when an error occurs

        Parameters
        ----------
        func : Callable, optional
            Callable object to process when retrieved error data.

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_error(lambda stream, event: display_response(stream, 'error', event))
        >>>
        >>> stream.open()
        """
        self._callbacks.on_error = func
        return self

    def on_complete(self, func: Callable):
        """
        This function called on complete event

        Parameters
        ----------
        func : Callable, optional
            Callable object to process when retrieved on complete data.

        Returns
        -------
        OMMStream
            current instance it is a OMM stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import omm_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = omm_stream.Definition("EUR")
        >>> stream = definition.get_stream()
        >>> stream.on_complete(lambda stream, event: display_response(stream, 'complete', event))
        >>>
        >>> stream.open()
        """
        self._callbacks.on_complete = func
        return self

    ###########################################
    # Process messages from stream connection #
    ###########################################
    def _on_refresh(self, message):
        with self.__item_stream_lock:
            self._status = message.get("State")
            stream_state = self._status.get("Stream")
            self._code = stream_state
            self._message = self._status.get("Text")

            super()._on_refresh(message)
            if not self.is_close:
                if self._callbacks.on_refresh:
                    try:
                        self._session.log(1, "OMMStream : call on_refresh callback")
                        self._callbacks.on_refresh(self, message)
                    except Exception as e:
                        self._session.log(
                            logging.ERROR,
                            f"OMMStream on_refresh callback raised exception: {e!r}",
                        )
                        self._session.log(1, f"{traceback.format_exc()}")

    def _on_status(self, status):
        with self.__item_stream_lock:
            state = status.get("State")
            stream_state = state.get("Stream")
            self._code = stream_state
            self._message = state.get("Text")

            if stream_state in ["Closed", "ClosedRecover", "NonStreaming", "Redirect"]:
                self.state = StreamState.Closed
                self._code = state.get("Code")
                self._session.log(
                    1, "Set stream {} as {}".format(self.stream_id, self._state)
                )
            if self._callbacks.on_status:
                try:
                    self._session.log(1, "OMMStream : call on_status callback")
                    self._callbacks.on_status(self, self.status)
                except Exception as e:
                    self._session.log(
                        logging.ERROR,
                        f"OMMStream on_status callback raised exception: {e!r}",
                    )
                    self._session.log(1, f"{traceback.format_exc()}")
            super()._on_status(status)

    def _on_update(self, update):
        with self.__item_stream_lock:
            super()._on_update(update)
            if self.state is not StreamState.Closed:
                if self._callbacks.on_update:
                    try:
                        self._session.log(1, "OMMStream : call on_update callback")
                        self._callbacks.on_update(self, update)
                    except Exception as e:
                        self._session.log(
                            logging.ERROR,
                            f"OMMStream on_update callback raised exception: {e!r}",
                        )
                        self._session.log(1, f"{traceback.format_exc()}")

    def _on_complete(self):
        with self.__item_stream_lock:
            super()._on_complete()
            if self.state is not StreamState.Closed:
                if self._callbacks.on_complete:
                    try:
                        self._session.log(1, "OMMStream : call on_complete callback")
                        self._callbacks.on_complete(self)
                    except Exception as e:
                        self._session.log(
                            logging.ERROR,
                            f"OMMStream on_complete callback raised exception: {e!r}",
                        )
                        self._session.log(1, f"{traceback.format_exc()}")

    def _on_error(self, error):
        with self.__item_stream_lock:
            super()._on_error(error)
            if self.state is not StreamState.Closed:
                self._message = error
                if self._callbacks.on_error:
                    try:
                        self._session.log(1, "OMMStream: call on_error callback")
                        self._callbacks.on_error(self, error)
                    except Exception as e:
                        self._session.log(
                            logging.ERROR,
                            f"OMMStream on_error callback raised an exception: {e!r}",
                        )
                        self._session.log(1, f"{traceback.format_exc()}")
