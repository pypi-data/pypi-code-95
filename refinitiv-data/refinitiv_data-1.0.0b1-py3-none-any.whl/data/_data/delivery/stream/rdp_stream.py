# coding: utf-8

import traceback
from threading import Lock
from typing import Callable

from ._rdp_stream import _RDPStream
from .rdp_stream_callback import RDPStreamCallback
from .state import StreamState


class RDPStream(_RDPStream):
    """
    Open an RDP stream.

    Parameters
    ----------

    service: string, optional
        name of RDP service

    universe: list
        RIC to retrieve item stream.

    view: list
        data fields to retrieve item stream

    parameters: dict
        extra parameters to retrieve item stream.

    api: string
        specific name of RDP streaming defined in config file. i.e. 'streaming/trading-analytics/redi'

    extended_params: dict, optional
        Specify optional params
        Default: None

    on_ack: callable object, optional
        Called when an ack is received.
        This callback receives an utf-8 string as argument.
        Default: None

    on_response: callable object, optional
        Called when an response is received.
        This callback receives an utf-8 string as argument.
        Default: None

    on_update: callable object, optional
        Called when an update is received.
        This callback receives an utf-8 string as argument.
        Default: None

    on_alarm: callable object, optional
        Called when an alarm is received.
        This callback receives an utf-8 string as argument.
        Default: None

    Raises
    ------
    Exception
        If request fails or if Refinitiv Services return an error

    Examples
    --------
    >>> import refinitiv.data as rd
    >>>
    >>> session = rd.session.platform.Definition(
                        app_key=APP_KEY,
                        grant=rd.session.platform.GrantPassword(
                            username=USERNAME,
                            password=PASSWORD,
                        )).get_session()
    >>> session.open()
    >>>
    >>> tds = rd.delivery.rdp_stream.Definition(
                        service=None,
                        universe=[],
                        view=None,
                        parameters={"universeType": "RIC"},
                        api='streaming/trading-analytics/redi').get_stream(session)
    >>> tds.open()
    """

    class Params(object):
        def __init__(self, *args, **kwargs):
            self._service = None
            self._universe = None
            self._view = None
            self._parameters = None
            self._session = None
            self._api = None
            self._extended_params = None
            self._on_ack = None
            self._on_response = None
            self._on_update = None
            self._on_alarm = None

            if len(args) > 0 and isinstance(args[0], RDPStream.Params):
                self.__init_from_params__(args[0])

            if kwargs:
                self._service = kwargs.get("service")
                self._universe = kwargs.get("universe")
                self._view = kwargs.get("view")
                self._parameters = kwargs.get("parameters")
                self._session = kwargs.get("session")
                self._api = kwargs.get("api")
                self._extended_params = kwargs.get("extended_params")
                self._on_ack = kwargs.get("on_ack")
                self._on_response = kwargs.get("on_response")
                self._on_update = kwargs.get("on_update")
                self._on_alarm = kwargs.get("on_alarm")

        def __init_from_params__(self, params):
            self._service = getattr(params, "service", None)
            self._universe = getattr(params, "universe", None)
            self._view = getattr(params, "view", None)
            self._parameters = getattr(params, "parameters", None)
            self._session = getattr(params, "session", None)
            self._api = getattr(params, "api", None)
            self._extended_params = getattr(params, "extended_params", None)
            self._on_ack = getattr(params, "on_ack", None)
            self._on_response = getattr(params, "on_response", None)
            self._on_update = getattr(params, "on_update", None)
            self._on_alarm = getattr(params, "on_alarm", None)

        def service(self, service: str):
            self._service = service
            return self

        def universe(self, universe: list):
            self._universe = universe
            return self

        def view(self, view: list):
            self._view = view
            return self

        def parameters(self, parameters: dict):
            self._parameters = parameters
            return self

        def session(self, session: object):
            self._session = session
            return self

        def api(self, api: str):
            self._api = api
            return self

        def with_extended_params(self, extended_params):
            self._extended_params = extended_params
            return self

        def on_ack(self, on_ack):
            self._on_ack = on_ack
            return self

        def on_response(self, on_response):
            self._on_response = on_response
            return self

        def on_update(self, on_update):
            self._on_update = on_update
            return self

        def on_alarm(self, on_alarm):
            self._on_alarm = on_alarm
            return self

    def __init__(
        self,
        session,
        service: str,
        universe: list,
        view: list,
        parameters: dict,
        api: str,
        extended_params=None,
        on_ack=None,
        on_response=None,
        on_update=None,
        on_alarm=None,
    ):
        _RDPStream.__init__(self, session, api)

        #   lock for callback function
        self.__item_stream_lock = Lock()

        #   set the RDP stream parameters
        #       set in the parent class
        self._service = service
        self._universe = universe
        self._view = view
        self._parameters = parameters

        #   RPD item stream parameters
        self._extended_params = extended_params

        #   callback functions
        self._callback = RDPStreamCallback(
            on_ack_cb=on_ack,
            on_response_cb=on_response,
            on_update_cb=on_update,
            on_alarm_cb=on_alarm,
        )

        #   last callback code and message
        self._message = None
        self._code = None

        #   validate parameters
        if self._session is None:
            raise AttributeError("Session must be defined")

    def _on_ack(self, ack):
        with self.__item_stream_lock:

            #   call parent class method
            super()._on_ack(ack)

            #   call callback function
            if self._callback.on_ack:
                self._session.debug("RDPStream : call on_ack callback.")
                try:
                    self._callback.on_ack(self, ack)
                except Exception as e:
                    self._session.error(
                        f"RDPStream on_ack callback raised exception: {e!r}"
                    )
                    self._session.debug(f"{traceback.format_exc()}")

    def _on_response(self, response):
        with self.__item_stream_lock:
            #   call parent class method
            super()._on_response(response)
            #   call callback function
            if self._callback.on_response:
                self._session.debug("RDPStream : call on_response callback.")
                try:
                    self._callback.on_response(self, response)
                except Exception as e:
                    self._session.error(
                        f"RDPStream on_response callback raised exception: {e!r}"
                    )
                    self._session.debug(f"{traceback.format_exc()}")

    def _on_update(self, update):
        with self.__item_stream_lock:
            #   call parent class method
            super()._on_update(update)

            #   call callback function
            if self._callback.on_update:
                self._session.debug("RDPStream : call on_update callback.")
                try:
                    self._callback.on_update(self, update)
                except Exception as e:
                    self._session.error(
                        f"RDPStream on_update callback raised exception: {e!r}"
                    )
                    self._session.debug(f"{traceback.format_exc()}")

    def _on_alarm(self, alarm):
        with self.__item_stream_lock:
            #   call parent class method
            super()._on_alarm(alarm)

            #   call callback function
            if self._callback.on_alarm:
                self._session.debug("RDPStream : call on_alarm callback.")
                try:
                    self._callback.on_alarm(self, alarm)
                except Exception as e:
                    self._session.error(
                        f"RDPStream on_alarm callback raised exception: {e!r}"
                    )
                    self._session.debug(f"{traceback.format_exc()}")

    #######################################
    #  methods to open and close session  #
    #######################################
    def open(self) -> StreamState:
        """
        Opens the RDPStream to start to stream. Once it's opened, it can be used in order to retrieve data.

        Parameters
        ----------

        Returns
        -------
        StreamState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> await stream.open_async()
        """
        return _RDPStream.open(self)

    async def open_async(self) -> StreamState:
        """
        Opens asynchronously the RDPStream to start to stream

        Parameters
        ----------

        Returns
        -------
        StreamState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> await stream.open_async()
        """
        return await _RDPStream.open_async(self)

    def close(self) -> StreamState:
        """
        Closes the RPDStream connection, releases resources

        Returns
        -------
        StreamState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.open()
        >>> stream.close()
        """
        return _RDPStream.close(self)

    async def close_async(self) -> StreamState:
        """
        Closes asynchronously the RPDStream connection, releases resources

        Returns
        -------
        StreamState
            current state of this RDP stream object.

        Examples
        --------
        >>> from refinitiv.data.delivery import rdp_stream
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.open()
        >>> await stream.close_async()
        """
        return await _RDPStream.close_async(self)

    #############################
    # RDPStream properties      #
    #############################

    def on_ack(self, on_ack: Callable):
        """
        This function called when the stream received an ack message.

        Parameters
        ----------
        func : Callable, optional
             Callable object to process retrieved ack data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_ack(lambda stream, event: display_response(stream, 'ack', event))
        >>>
        >>> stream.open()
        """
        self._callback.on_ack = on_ack
        return self

    def on_response(self, on_response):
        """
        This function called when the stream received an response message.

        Parameters
        ----------
        func : Callable, optional
             Callable object to process retrieved response data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_response(lambda stream, event: display_response(stream, 'response', event))
        >>>
        >>> stream.open()
        """
        self._callback.on_response = on_response
        return self

    def on_update(self, on_update):
        """
        This function called when the stream received an update message.

        Parameters
        ----------
        func : Callable, optional
             Callable object to process retrieved update data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_update(lambda stream, event: display_response(stream, 'update', event))
        >>>
        >>> stream.open()
        """
        self._callback.on_update = on_update
        return self

    def on_alarm(self, on_alarm):
        """
        This function called when the stream received an alarm message.

        Parameters
        ----------
        func : Callable, optional
             Callable object to process retrieved alarm data

        Returns
        -------
        RDPStream
            current instance it is a RDP stream object.

        Examples
        --------
        Prerequisite: The default session must be opened.
        >>> from datetime import datetime
        >>> from refinitiv.data.delivery import rdp_stream
        >>>
        >>> def display_response(response, event_type, event):
                print(f'{response} - {event_type} received at {datetime.now}')
                print(event)
        >>>
        >>> definition = rdp_stream.Definition(
                                service=None,
                                universe=[],
                                view=None,
                                parameters={"universeType": "RIC"},
                                api='streaming/trading-analytics/redi')
        >>> stream = definition.get_stream()
        >>> stream.on_alarm(lambda stream, event: display_response(stream, 'alarm', event))
        >>>
        >>> stream.open()
        """
        self._callback.on_alarm = on_alarm
        return self
