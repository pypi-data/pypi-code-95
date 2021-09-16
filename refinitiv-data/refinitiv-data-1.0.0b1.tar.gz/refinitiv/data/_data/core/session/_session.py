# coding: utf-8

__all__ = ["Session", "DacsParams"]

import abc
import asyncio
import itertools
import logging
import socket
import traceback
import warnings
from enum import Enum, unique
from threading import Lock
from typing import Callable

import httpx
import nest_asyncio
import requests_async
import urllib3.exceptions
import validators

from ._omm_stream_listener import OMMStreamListener
from ._omm_stream_listener._omm_stream_listener_manager import OMMStreamObserver
from ._session_cxn_type import SessionCxnType
from ._session_state import SessionState
from ._streaming_chain_listener import StreamingChainListener
from ._streaming_chain_listener._streaming_chain_listener_manager import (
    StreamingChainObserver,
)
from ._timeout_adapter import TimeoutRetry, AsyncHTTPAdapter
from ... import configure
from ... import log
from ...delivery.stream import StreamState
from ...delivery.stream import StreamingServiceDirectory
from ...errors import SessionError
from ...tools._common import urljoin, cached_property
from ...tools._repr_definition import create_str_definition

# Load nest_asyncio to allow multiple calls to run_until_complete available
nest_asyncio.apply()


class DacsParams(object):
    def __init__(self, *args, **kwargs):
        self.deployed_platform_username = kwargs.get(
            "deployed_platform_username", "user"
        )
        self.dacs_application_id = kwargs.get("dacs_application_id", "256")
        self.dacs_position = kwargs.get("dacs_position")
        if self.dacs_position in [None, ""]:
            try:
                position_host = socket.gethostname()
                self.dacs_position = "{}/{}".format(
                    socket.gethostbyname(position_host), position_host
                )
            except socket.gaierror:
                self.dacs_position = "127.0.0.1/net"
        self.authentication_token = kwargs.get("authentication_token")


class Session(abc.ABC, OMMStreamObserver, StreamingChainObserver):
    _DUMMY_STATUS_CODE = -1
    _id_iterator = itertools.count()
    # Logger for messages outside of particular session instances
    class_logger = log.create_logger("session")

    @unique
    class EventCode(Enum):
        """
        Each session can report different status events during it's lifecycle.
            StreamConnecting : Denotes the connection to the stream service within the session is pending.
            StreamConnected : Denotes the connection to the stream service has been successfully established.
            StreamDisconnected : Denotes the connection to the stream service is not established.
            SessionAuthenticationSuccess : Denotes the session has successfully authenticated this client.
            SessionAuthenticationFailed : Denotes the session has failed to authenticate this client.
            StreamAuthenticationSuccess: Denotes the stream has successfully authenticated this client.
            StreamAuthenticationFailed: Denotes the stream has failed to authenticate this client.
            DataRequestOk : The request for content from the session data services has completed successfully.
            DataRequestFailed : The request for content from the session data services has failed.
        """

        StreamConnecting = 1
        StreamConnected = 2
        StreamDisconnected = 3
        StreamAuthenticationSuccess = 4
        StreamAuthenticationFailed = 5
        StreamReconnecting = 6

        SessionConnecting = 21
        SessionConnected = 22
        SessionDisconnected = 23
        SessionAuthenticationSuccess = 24
        SessionAuthenticationFailed = 25
        SessionReconnecting = 26

        DataRequestOk = 61
        DataRequestFailed = 62

    class Params(object):
        def __init__(self, app_key=None, on_event=None, on_state=None, **kwargs):
            self._app_key = app_key
            self._on_event_cb = on_event
            self._on_state_cb = on_state
            self._dacs_params = DacsParams()

        def app_key(self, app_key):
            if app_key is None:
                raise ValueError("app_key value can't be None")
            self._app_key = app_key
            return self

        def with_deployed_platform_username(self, user):
            if user:
                self._dacs_params.deployed_platform_username = user
            return self

        def with_dacs_application_id(self, application_id):
            if application_id:
                self._dacs_params.dacs_application_id = application_id
            return self

        def with_dacs_position(self, position):
            if position:
                self._dacs_params.dacs_position = position
            return self

        def on_state(self, on_state):
            self._on_state_cb = on_state
            return self

        def on_event(self, on_event):
            self._on_event_cb = on_event
            return self

    __all_sessions = {}
    __register_session_lock = Lock()
    __acquire_session_id_lock = Lock()

    @classmethod
    def register_session(cls, session):
        with cls.__register_session_lock:

            if not session:
                raise SessionError("Error", "Try to register not session")

            session_id = session.session_id

            if session_id in cls.__all_sessions:
                return

            cls.__all_sessions[session.session_id] = session

    @classmethod
    def unregister_session(cls, session):
        with cls.__register_session_lock:

            if not session:
                raise SessionError(1, "Try to unregister not session")

            session_id = session.session_id

            if session_id is None:
                raise SessionError(
                    1, "Try to unregister session with session_id is None"
                )

            if session_id not in cls.__all_sessions:
                raise SessionError(
                    1, f"Try to unregister unknown session id {session_id}"
                )

            cls.__all_sessions.pop(session_id)

    @classmethod
    def get_session(cls, session_id):
        """
        Returns the stream session singleton
        """
        if session_id not in cls.__all_sessions:
            raise SessionError(
                "Error", "Try to get unknown session id {}".format(session_id)
            )
        return cls.__all_sessions.get(session_id)

    @property
    def name(self):
        return self._name

    def __init__(
        self,
        app_key,
        on_state=None,
        on_event=None,
        token=None,
        deployed_platform_username=None,
        dacs_position=None,
        dacs_application_id=None,
        session_name="default-session",
    ):
        with self.__acquire_session_id_lock:
            self._session_id = next(self._id_iterator)
        session_type = self.type.name.lower()
        logger_name = f"sessions.{session_type}.{session_name}.{self.session_id}"
        self.class_logger.debug(
            f'Creating session "{logger_name}" based on '
            f'session.{session_type}.Definition("{session_type}.{session_name}")'
        )

        if app_key is None:
            raise ValueError("app_key value can't be None")

        OMMStreamObserver.__init__(self, self)
        StreamingChainObserver.__init__(self, self)

        self._lock_log = Lock()

        self._state = SessionState.Closed
        self._status = Session.EventCode.StreamDisconnected
        self._last_event_code = None
        self._last_event_message = None

        self._last_stream_connection_name = None

        self._app_key = app_key
        self._on_event_cb = on_event
        self._on_state_cb = on_state
        self._access_token = token
        self._dacs_params = DacsParams()

        if deployed_platform_username:
            self._dacs_params.deployed_platform_username = deployed_platform_username
        if dacs_position:
            self._dacs_params.dacs_position = dacs_position
        if dacs_application_id:
            self._dacs_params.dacs_application_id = dacs_application_id

        self._logger = log.create_logger(logger_name)
        # redirect log method of this object to the log in logger object
        self.log = self._logger.log
        self.warning = self._logger.warning
        self.error = self._logger.error
        self.debug = self._logger.debug
        self.info = self._logger.info

        self._name = session_name

        ############################################################
        #   multi-websockets support

        #   a mapping dictionary between the stream connection name -> stream connection obj
        self._stream_connection_name_to_stream_connection_dict = {}

        ############################################################
        #   stream connection auto-reconnect support

        #   a mapping dictionary between the stream connection name -> a list of stream ids
        self._stream_connection_name_to_stream_ids_dict = {}

        # parameters for stream websocket
        try:
            self._loop = asyncio.get_event_loop()
            self.log(1, f"Session loop was set to current event loop {self._loop}")
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            self.log(1, f"Session loop was set with a new event loop {self._loop}")

        nest_asyncio.apply(self._loop)

        self.__lock_callback = Lock()
        self._httpx_async_client = None
        self._http_session_auto_retry_client = None

        self._stream_register_lock = Lock()
        self._all_stream_subscriptions = {}

        self._request_new_stream_id_lock = Lock()
        self._set_stream_authentication_token_lock = Lock()

        # for OMMStreamListener
        self._all_omm_item_stream = dict()
        self._all_omm_stream_listeners = dict()

        # for StreamingChainListener
        self._all_streaming_chains = dict()
        self._all_chains_listeners = dict()

        self._id_request = 0

        # for service directory
        self._service_directories = []

        configure.config.on(configure.ConfigEvent.UPDATE, self._on_config_updated)

    @cached_property
    def _connection(self) -> "SessionConnection":
        from ._session_cxn_factory import get_session_cxn

        return get_session_cxn(self._get_session_cxn_type(), self)

    @abc.abstractmethod
    def _get_session_cxn_type(self) -> SessionCxnType:
        pass

    def on_state(self, callback: Callable) -> None:
        """
        On state callback
        Parameters
        ----------
            callback: Callable
                Callback function or method

        Raises
        ----------
        Exception
            If user provided invalid object type

        """
        if not callable(callback):
            raise TypeError("Please provide callable object")

        self._on_state_cb = callback

    def on_event(self, callback: Callable) -> None:
        """
        On event callback
        Parameters
        ----------
            callback: Callable
                Callback function or method

        Raises
        ----------
        Exception
            If user provided invalid object type
        """
        if not callable(callback):
            raise TypeError("Please provide callable object")
        self._on_event_cb = callback

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="session",
            content=f"{{session_name='{self.name}'}}",
        )

    def _on_config_updated(self):
        log_level = log.read_log_level_config()

        if log_level != self.get_log_level():
            self.set_log_level(log_level)

    def __del__(self):
        configure.config.remove_listener(
            configure.ConfigEvent.UPDATE, self._on_config_updated
        )

        if hasattr(self, "_logger"):
            log.dispose_logger(self._logger)

    def __delete__(self, instance):
        self.log(1, f"Delete the Session instance {instance}")

    def run_until_complete(self, future):
        return self._loop.run_until_complete(future)

    def call_soon_threadsafe(self, callback, *args):
        return self._loop.call_soon_threadsafe(callback, *args)

    def has_same_loop(self, loop=None):
        cur_loop = asyncio.get_event_loop()
        loop = loop or cur_loop
        return self._loop == loop

    def _set_proxy(self, http, https):
        pass

    def get_open_state(self):
        """
        Returns the session state.
        """
        return self._state

    @property
    def is_closed(self):
        return self._state == SessionState.Closed

    @property
    def is_open(self):
        return self._state == SessionState.Open

    def get_last_event_code(self):
        """
        Returns the last session event code.
        """
        return self._last_event_code

    def get_last_event_message(self):
        """
        Returns the last event message.
        """
        return self._last_event_message

    @property
    def app_key(self):
        """
        Returns the application id.
        """
        return self._app_key

    @app_key.setter
    def app_key(self, app_key):
        """
        Set the application key.
        """
        from ...legacy.tools import is_string_type

        if app_key is None:
            return
        if not is_string_type(app_key):
            raise AttributeError("application key must be a string")

        self._app_key = app_key

    def set_access_token(self, access_token):
        self.debug(f"Session.set_access_token()")
        self._access_token = access_token

    def set_stream_authentication_token(self, stream_authentication_token):
        """Set the authentication token to all stream connections"""
        try:
            self.debug(f"Session.set_stream_authentication_token()")

            with self._set_stream_authentication_token_lock:
                #   loop over all stream connection and set authentication token
                for (
                    stream_connection
                ) in self._stream_connection_name_to_stream_connection_dict.values():
                    self.debug(
                        f"      forwarding the authentication token to stream connection : {stream_connection}"
                    )
                    #   set the authentication token
                    if stream_connection.is_alive():
                        #   stream connection still alive, so forward the new authentication token
                        stream_connection.set_stream_authentication_token(
                            stream_authentication_token
                        )

                    self.debug("DONE :: Session.set_stream_authentication_token()")

        except Exception as e:
            self.error(
                f"ERROR!!! session cannot set stream authentication token.\n{e!r}"
            )
            raise e

    def request_stream_authentication_token(self):
        """The function is used for requesting new stream authentication token.
        note that currently only Platform session has this functionality.
        """
        pass

    @property
    def session_id(self):
        return self._session_id

    def logger(self):
        return self._logger

    def _get_rdp_url_root(self):
        return ""

    @property
    def http_request_timeout_secs(self):
        """the default http request timeout in secs"""
        key = configure.keys.http_request_timeout
        value = configure.get(key)

        is_list = isinstance(value, list)
        if is_list and len(value) == 1:
            value = value[0]
            try:
                value = int(value)
            except ValueError:
                pass

        number = isinstance(value, int) or isinstance(value, float)
        negative_number = number and value < 0

        if number and value == 0:
            value = None
        elif number and value == 1:
            value = 1

        is_none = value is None

        set_default = not is_none and (not number or negative_number)
        print_warn = not is_none and (not number or negative_number)

        if set_default:
            value = configure.defaults.http_request_timeout

        if print_warn:
            self.warning(f"Invalid value of the {key}. Default value is used")

        return value

    def _get_endpoint_config(self, name):
        """get a specific endpoint config"""

        #   get an endpoint data from config file
        endpoint_config = configure.get(f"apis.{name}", None)
        assert endpoint_config is not None
        self.debug(f"endpoint config for {name} is {endpoint_config}")

        #   done
        return endpoint_config

    def get_subscription_streams(self, stream_event_id):
        """get a list of streams that subscription to given id"""
        with self._stream_register_lock:
            if stream_event_id is None:
                raise SessionError(1, "Try to retrieve undefined stream")
            if stream_event_id in self._all_stream_subscriptions:
                return [
                    self._all_stream_subscriptions[stream_event_id],
                ]
            return []

    def get_subscription_streams_by_service(self, stream_connection_name: str):
        """get a lost of streams that subscription on given stream service"""
        with self._stream_register_lock:
            #   get a list of stream ids that subscribe to given stream service
            stream_ids = self._stream_connection_name_to_stream_ids_dict.get(
                stream_connection_name, []
            )

            #   mapping stream ids to stream objs
            subscription_streams = []
            for stream_id in stream_ids:
                #   get the stream obj from id
                assert stream_id in self._all_stream_subscriptions
                stream = self._all_stream_subscriptions[stream_id]

                #   append the stream to the list
                subscription_streams.append(stream)

            #   done
            return subscription_streams

    ############################################################
    #   reconnection configuration

    @property
    def stream_auto_reconnection(self):
        return True

    @property
    def server_mode(self):
        return False

    ############################################################
    #   configuration

    def _get_streaming_connection_config_name_and_endpoint_name(
        self, streaming_connection_name: str
    ):
        """
        Parameters
        ----------
        stream_connection_name
            a name of stream connection in the config file i.e. "streaming/pricing/main"

        Returns
        --------
        tuple
            the streaming connection config name and endpoint name
        """

        try:
            (
                streaming,
                streaming_name,
                endpoint_name,
            ) = streaming_connection_name.split("/")
        except ValueError:
            raise Exception(
                f"'streaming_connection_name' format: "
                f"'{{streaming}}/{{streaming_name}}/{{endpoint_name}}'\n"
                f"Recived: {streaming_connection_name}"
            )

        assert streaming == "streaming"

        #   build the streaming connection config string
        streaming_connection_config_name = f"apis.streaming.{streaming_name}"
        streaming_connection_config_endpoint_name = (
            f"{streaming_connection_config_name}.endpoints.{endpoint_name}"
        )

        #   done
        return (
            streaming_connection_config_name,
            streaming_connection_config_endpoint_name,
        )

    def get_streaming_protocols(self, streaming_connection_name: str):
        """
        Parameters
        ----------
        stream_connection_name
            a name of stream connection in the config file i.e. "streaming/pricing/main"

        Returns
        --------
        str
            a list of protocol
        """

        #   get streaming connection config name
        (
            streaming_connection_config_name,
            streaming_connection_config_endpoint_name,
        ) = self._get_streaming_connection_config_name_and_endpoint_name(
            streaming_connection_name
        )

        try:
            streaming_connection_protocols = configure.config.get_list(
                f"{streaming_connection_config_endpoint_name}.protocols"
            )
        except KeyError as e:
            raise Exception(
                f"Can't find protocols in configuration "
                f"for '{streaming_connection_config_endpoint_name}'"
            )

        #   done
        return streaming_connection_protocols

    def get_streaming_websocket_endpoint_url(self, streaming_connection_name: str):
        """
        Parameters
        ----------
        stream_connection_name
            a name of stream connection in the config file i.e. "streaming/pricing/main"

        Returns
        --------
        str
            the stream discovery endpoint of given streaming connection name
        """

        #   get streaming connection config name
        (
            streaming_connection_config_name,
            streaming_connection_config_endpoint_name,
        ) = self._get_streaming_connection_config_name_and_endpoint_name(
            streaming_connection_name
        )

        #   retrieve the endpoint from config file
        #       websocket url
        try:
            streaming_connection_endpoint_websocket_path = configure.config.get_str(
                f"{streaming_connection_config_endpoint_name}.websocket-url"
            )
        except KeyError:
            streaming_connection_endpoint_websocket_path = None

        #   done
        return streaming_connection_endpoint_websocket_path

    def get_streaming_discovery_endpoint_url(self, streaming_connection_name: str):
        """
        Parameters
        ----------
        stream_connection_name
            a name of stream connection in the config file i.e. "streaming/pricing/main"

        Returns
        --------
        tuple
            the stream discovery endpoint of given streaming connection name
        """
        from ... import configure

        #   get streaming connection config name
        (
            streaming_connection_config_name,
            streaming_connection_config_endpoint_name,
        ) = self._get_streaming_connection_config_name_and_endpoint_name(
            streaming_connection_name
        )

        #   retrieve the endpoint from config file
        #       base streaming url
        try:
            streaming_connection_path = configure.config.get_str(
                f"{streaming_connection_config_name}.url"
            )
        except KeyError:
            self.debug(
                f"Can't find url for {streaming_connection_config_name}"
                f" in cofiguration"
            )

            streaming_connection_path = None

        try:
            streaming_connection_endpoint_path = configure.config.get_str(
                f"{streaming_connection_config_endpoint_name}.path"
            )
        except KeyError:
            self.debug(
                f"Can't find path for {streaming_connection_config_endpoint_name}"
                f" in configuration"
            )

            streaming_connection_endpoint_path = None

        self.debug(
            f"     building the streaming endpoint..........\n"
            f"             base streaming path    = {streaming_connection_path}\n"
            f"             endpoint path          = {streaming_connection_endpoint_path}"
        )

        #   build the stream discovery endpoint url
        if (
            streaming_connection_path is not None
            and streaming_connection_endpoint_path is not None
        ):
            #   build the stream discovery endpoint
            streaming_connection_path = streaming_connection_path.strip()
            if streaming_connection_path.startswith("/"):
                stream_connection_url = urljoin(
                    self._get_rdp_url_root(), streaming_connection_path
                )
            elif validators.url(streaming_connection_path):
                self.debug(
                    f"    override discovery endpoint \t= {self._get_rdp_url_root()}"
                )
                stream_connection_url = streaming_connection_path
            else:
                self.error(f"    invalid discovery url \t= {streaming_connection_path}")
                raise ValueError(f"Not correct the url: \t {streaming_connection_path}")

            return urljoin(stream_connection_url, streaming_connection_endpoint_path)
        else:
            #   invalid discovery endpoint
            return None

    ############################################################
    #   multi-WebSockets support

    @abc.abstractmethod
    def _get_stream_status(self, stream_connection_name: str):
        """
        This method is designed for getting a status of given stream service.
        Parameters
        ----------
            a name of stream connection
        Returns
        -------
        enum
            status of stream service.
        """
        pass

    @abc.abstractmethod
    def _set_stream_status(self, stream_connection_name: str, stream_status):
        """
        Set status of given stream service
        Parameters
        ----------
        stream_connection_name
            a name of stream connection
        stream_status
            a status enum of stream
        Returns
        -------
        """
        pass

    @abc.abstractmethod
    def get_omm_login_message_key_data(self):
        """return the login message for OMM 'key' section"""
        pass

    @abc.abstractmethod
    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP protocol"""
        pass

    ######################################
    # methods to manage log              #
    ######################################
    def set_log_level(self, log_level: [int, str]) -> None:
        """
        Set the log level.
        By default, logs are disabled.

        Parameters
        ----------
        log_level : int, str
            Possible values from logging module :
            [CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET]
        """
        log_level = log.convert_log_level(log_level)
        self._logger.setLevel(log_level)

        if log_level <= logging.DEBUG:
            # Enable debugging
            self._loop.set_debug(True)

            # Make the threshold for "slow" tasks very very small for
            # illustration. The default is 0.1, or 100 milliseconds.
            self._loop.slow_callback_duration = 0.001

            # Report all mistakes managing asynchronous resources.
            warnings.simplefilter("always", ResourceWarning)

    def get_log_level(self):
        """
        Returns the log level
        """
        return self._logger.level

    def trace(self, message):
        self._logger.log(log.TRACE, message)

    ######################################
    # methods to open and close session  #
    ######################################
    def open(self) -> SessionState:
        """open session

        do an initialization config file, and http session if it's necessary.

        Returns
        -------
        SessionState
            the current state of this session.
        """
        if self._state in [SessionState.Pending, SessionState.Open]:
            # session is already opened or is opening
            return self._state
        configure.config.remove_listener(
            configure.ConfigEvent.UPDATE, self._on_config_updated
        )
        configure.config.on(configure.ConfigEvent.UPDATE, self._on_config_updated)

        self._httpx_async_client = httpx.AsyncClient()
        # Config for http auto-retry
        key = configure.keys.http_auto_retry_config
        auto_retry_config = configure.get(key, None)
        if auto_retry_config:
            # currently, "enabled" is not yet exposed in auto-retry config, by default it's enabled
            auto_retry_enabled = True  # auto_retry_config.get("enabled", True)
            number_of_retries = auto_retry_config.get("number-of-retries", 3)
            retry_on_errors = auto_retry_config.get("on-errors", [])
            retry_backoff_factor = auto_retry_config.get("backoff-factor", 1)
            retry_on_methods = auto_retry_config.get("on-methods", ["GET", "POST"])

            self._http_session_auto_retry_client = requests_async.Session()
            retry_strategy = TimeoutRetry(
                session=self,
                timeout=self.http_request_timeout_secs,
                total=number_of_retries,
                status_forcelist=retry_on_errors,
                allowed_methods=retry_on_methods,
                backoff_factor=retry_backoff_factor,
            )

            adapter = AsyncHTTPAdapter(
                max_retries=retry_strategy, timeout=self.http_request_timeout_secs
            )
            self._http_session_auto_retry_client.mount("https://", adapter)
            self._http_session_auto_retry_client.mount("http://", adapter)
        else:
            auto_retry_enabled = False

        self._loop.run_until_complete(self.open_async())
        return self._state

    def close(self) -> SessionState:
        """
        Close platform/desktop session

        Returns
        -------
        State
        """
        if self._state == SessionState.Closed:
            return self._state

        if not self._loop.is_closed():
            return self._loop.run_until_complete(self.close_async())
        else:
            return self._close()

    async def open_async(self) -> SessionState:
        Session.register_session(self)
        return self._state

    async def close_async(self) -> SessionState:
        await self._stop_streaming()
        return self._close()

    def _close(self) -> SessionState:
        self._state = SessionState.Closed
        # close all listeners
        self.close_all_omm_streams()
        self.close_all_streaming_chains()
        Session.unregister_session(self)
        configure.config.remove_listener(
            configure.ConfigEvent.UPDATE, self._on_config_updated
        )
        self._loop.run_until_complete(self._httpx_async_client.aclose())
        self._httpx_async_client = None

        if self._http_session_auto_retry_client:
            self._loop.run_until_complete(self._http_session_auto_retry_client.close())
            self.__http_session_auto_retry_client = None

        return self._state

    async def wait_for_streaming_reconnection(
        self, stream_connection_name: str, connection_protocol_name: str = None
    ):
        """wait for a streaming reconnection
        Return True if the reconnection is successfully, otherwise False
        """
        #   retrieve the stream connection
        stream_connection = self._stream_connection_name_to_stream_connection_dict[
            stream_connection_name
        ]

        # assert that stream_connection thread is alive
        assert stream_connection.is_alive()

        #   wait for stream connection is ready
        ready_future = stream_connection.ready

        try:
            await ready_future
        except asyncio.CancelledError:
            #   the stream connection is failed to reconnect
            return False

        #   done, connection is ready
        return True

    async def wait_for_streaming(self, api: str, protocol_name: str):
        await self._start_streaming(api, protocol_name)
        status = self._get_stream_status(api)
        if status is Session.EventCode.StreamConnected:
            return True
        else:
            self.debug("Streaming failed to start")
            return False

    async def _start_streaming(self, api: str, protocol_name: str):
        """
        Start the stream connection via WebSocket if the connection doesn't exist,
        otherwise waiting unit the stream connection is ready.
        note that the default connection_protocol is 'OMM'

        RAISES
            SessionError if library cannot establish the WebSocket connection.
        """

        status = self._get_stream_status(api)

        if status not in [
            Session.EventCode.StreamConnected,
            Session.EventCode.StreamConnecting,
            Session.EventCode.StreamReconnecting,
        ]:
            self._set_stream_status(api, Session.EventCode.StreamConnecting)
            from ...delivery.stream._stream_cxn_factory import (
                get_stream_cxn,
                convert_api_to_stream_cxn_type,
                get_protocol_type_by_name,
            )

            stream_cxn_type = convert_api_to_stream_cxn_type(api)
            protocol_type = get_protocol_type_by_name(protocol_name)
            stream_cxn = get_stream_cxn(
                stream_cxn_type, protocol_type, self, self.type, api
            )

            self._stream_connection_name_to_stream_connection_dict[api] = stream_cxn
        else:
            stream_cxn = self._stream_connection_name_to_stream_connection_dict[api]

        try:
            await stream_cxn.ready
        except asyncio.CancelledError:
            self.error("Streaming connection cannot connect to WebSocket host.")
            self._set_stream_status(api, Session.EventCode.StreamDisconnected)
            self.debug("waiting for streaming connection thread terminate properly.")
            stream_cxn.join()

            raise SessionError(
                -1,
                f"ERROR!!! CANNOT establish the WebSocket connection for {api}",
            )

        status = self._get_stream_status(api)
        return status

    def _start_service_directory(self, stream_connection_name: str):
        if self._metadata_service:
            return self._met

        if stream_connection_name not in self._service_directory:
            self._service_directories[
                stream_connection_name
            ] = StreamingServiceDirectory(self, stream_connection_name)

        status = self._get_stream_status(stream_connection_name)
        if status is Session.EventCode.StreamConnected:
            # Subscribe for Services
            self._service_directories[stream_connection_name].open()
            return True
        else:
            self.debug(
                f"Can't start service directory because {stream_connection_name} is closed"
            )
            return False

    def send(self, stream_connection_name: str, message):
        """
        Send message to the corresponding stream service
        """

        #   get the stream connection corresponding to the stream service
        stream_connection = self._stream_connection_name_to_stream_connection_dict.get(
            stream_connection_name, None
        )
        if stream_connection:
            #   found the stream connect corresponding to stream service, so send the message via this stream connection
            stream_connection.send(message)
        else:
            #   session doesn't have any stream connection of given stream service
            self.error(
                f'ERROR!!! session does not has a stream service "{stream_connection_name}".'
            )

    def is_closing(self, stream_connection_name: str):
        assert (
            stream_connection_name
            in self._stream_connection_name_to_stream_connection_dict
        )
        return self._stream_connection_name_to_stream_connection_dict[
            stream_connection_name
        ].is_closing

    async def _stop_streaming(self):
        for (
            api,
            connection,
        ) in self._stream_connection_name_to_stream_connection_dict.items():
            self.debug(f'closing the stream connection "{api}"')
            await connection.close_async()

            self._set_stream_status(api, Session.EventCode.StreamDisconnected)

            streams = self.get_subscription_streams_by_service(api)
            for stream in streams:
                stream.close()

        self._status = Session.EventCode.StreamDisconnected

    ##########################################################
    # methods for listeners subscribe / unsubscribe          #
    ##########################################################
    def subscribe(self, listener, with_updates=True):
        if isinstance(listener, OMMStreamListener):
            return self._subscribe_omm_stream(
                omm_stream_listener=listener, with_updates=with_updates
            )

        if isinstance(listener, StreamingChainListener):
            return self._subscribe_streaming_chain(
                chain_listener=listener, with_updates=with_updates
            )

    async def subscribe_async(self, listener, with_updates=True):
        if isinstance(listener, OMMStreamListener):
            return await self._subscribe_omm_stream_async(
                omm_stream_listener=listener, with_updates=with_updates
            )

        if isinstance(listener, StreamingChainListener):
            return await self._subscribe_streaming_chain_async(
                chain_listener=listener, with_updates=with_updates
            )

    def unsubscribe(self, listener):
        if isinstance(listener, OMMStreamListener):
            self._unsubscribe_omm_stream(listener)

        if isinstance(listener, StreamingChainListener):
            self._unsubscribe_streaming_chain(chain_listener=listener)

    async def unsubscribe_async(self, listener):
        if isinstance(listener, OMMStreamListener):
            await self.__unsubscribe_omm_stream_async(listener)

        if isinstance(listener, StreamingChainListener):
            await self._unsubscribe_streaming_chain_async(chain_listener=listener)

    ##########################################################
    # Methods for stream register / unregister               #
    ##########################################################
    def _get_new_id(self):
        with self._request_new_stream_id_lock:
            self._id_request += 1
        return self._id_request

    def _register_stream(self, stream):
        with self._stream_register_lock:
            if stream is None:
                raise SessionError(1, "Try to register None subscription.")

            stream_id = stream.stream_id
            if stream_id in self._all_stream_subscriptions:
                if self._check_omm_item_stream(stream):
                    return

                raise SessionError(
                    1, f"Subscription {stream_id} is already registered."
                )

            stream_api = stream.api
            if stream_api is None:
                raise SessionError(
                    1,
                    f"Try to register but given stream[{stream_id}] has api property is None.",
                )

            if stream_id is None:
                stream_id = self._get_new_id()
                stream.stream_id = stream_id

            self._all_stream_subscriptions[stream_id] = stream

            stream_ids = self._stream_connection_name_to_stream_ids_dict.setdefault(
                stream_api, []
            )
            stream_ids.append(stream_id)

    def _unregister_stream(self, stream):
        with self._stream_register_lock:
            if stream is None:
                raise SessionError(
                    1, "Try to un-register unavailable stream: stream is None."
                )

            stream_id = stream.stream_id
            if stream_id is None:
                raise SessionError(
                    1, "Try to un-register unavailable stream: stream_id is None."
                )

            if not self._all_stream_subscriptions:
                return

            if stream_id not in self._all_stream_subscriptions:
                raise SessionError(
                    1,
                    f"Try to un-register unknown stream[{stream_id}] "
                    f"from session {self.session_id}.",
                )

            stream_api = stream.api
            if stream_api is None:
                raise SessionError(
                    1,
                    f"Try to un-register but given stream[{stream_id}] has api property is None.",
                )

            if stream_api not in self._stream_connection_name_to_stream_ids_dict:
                raise SessionError(
                    1,
                    f"Try to un-register unknown stream api[{stream_api}] of stream[{stream_id}].",
                )

            stream_ids = self._stream_connection_name_to_stream_ids_dict[stream_api]
            stream_ids.remove(stream_id)
            self._all_stream_subscriptions.pop(stream_id)

    def _get_stream(self, stream_id):
        with self._stream_register_lock:
            if stream_id is None:
                raise SessionError("Error", "Try to retrieve undefined stream")
            if stream_id in self._all_stream_subscriptions:
                return self._all_stream_subscriptions[stream_id]
            return None

    ##########################################################
    # methods for session callbacks from streaming session   #
    ##########################################################
    def _on_open(self):
        with self.__lock_callback:
            self._state = SessionState.Pending

    def _on_close(self):
        with self.__lock_callback:
            self._state = SessionState.Closed

    def _on_state(self, state_code, state_text):
        with self.__lock_callback:
            if isinstance(state_code, SessionState):
                self._state = state_code
                if self._on_state_cb is not None:
                    try:
                        self._on_state_cb(self, state_code, state_text)
                    except Exception as e:
                        self.error(
                            f"on_state user function on session {self.session_id} raised error {e}"
                        )

    def _on_event(
        self,
        event_code,
        event_msg,
        streaming_session_id=None,
        stream_connection_name=None,
    ):
        self.debug(
            f"Session._on_event("
            f"event_code={event_code}, "
            f"event_msg={event_msg}, "
            f"streaming_session_id={streaming_session_id}, "
            f"stream_connection_name={stream_connection_name})"
        )
        with self.__lock_callback:
            #   check the on_event trigger from some of the stream connection or not?
            if stream_connection_name:
                #   this on_event come form stream connection
                assert (
                    stream_connection_name
                    in self._stream_connection_name_to_stream_connection_dict
                )
                stream_connection = (
                    self._stream_connection_name_to_stream_connection_dict.get(
                        stream_connection_name, None
                    )
                )

                #   validate the event for this session
                if stream_connection:
                    #   valid session that contain the stream connection for this event
                    if (
                        streaming_session_id
                        and stream_connection.streaming_session_id
                        == streaming_session_id
                    ):

                        #   for session event code
                        if isinstance(event_code, Session.EventCode):
                            #   store the event code to the corresponding stream service
                            self._set_stream_status(stream_connection_name, event_code)

                            #   call the callback function
                            if self._on_event_cb:
                                try:
                                    self._on_event_cb(self, event_code, event_msg)
                                except Exception as e:
                                    self.error(
                                        f"on_event user function on session {self.session_id} raised error {e}"
                                    )
                    else:
                        self.debug(
                            f"Received notification "
                            f"from another streaming session ({streaming_session_id}) "
                            f"than current one ({stream_connection.streaming_session_id})"
                        )
                else:
                    self.debug(
                        f"Received notification for closed streaming session {streaming_session_id}"
                    )
            else:
                #   not stream connection on_event, just call the on_event callback
                #   call the callback function
                if self._on_event_cb:
                    try:
                        self._on_event_cb(self, event_code, event_msg)
                    except Exception as e:
                        self.error(
                            f"on_event user function on session {self.session_id} raised error {e}"
                        )

    def process_on_close_event(self):
        self.close()

    ##############################################
    # methods for status reporting               #
    ##############################################
    @staticmethod
    def _report_session_status(self, session, session_status, event_msg):
        _callback = self._get_status_delegate(session_status)
        if _callback is not None:
            json_msg = self._define_results(session_status)[Session.CONTENT] = event_msg
            _callback(session, json_msg)

    def report_session_status(self, session, event_code, event_msg):
        # Report the session status event defined with the eventMsg to the appropriate delegate
        self._last_event_code = event_code
        self._last_event_message = event_msg
        _callback = self._get_status_delegate(event_code)
        if _callback is not None:
            try:
                _callback(session, event_code, event_msg)
            except Exception as e:
                self._session.error(
                    f"{self.__name__} on_event or on_state callback raised exception: {e!r}"
                )
                self._session.debug(f"{traceback.format_exc()}")

    def _get_status_delegate(self, event_code):
        _cb = None

        if event_code in [
            Session.EventCode.SessionAuthenticationSuccess,
            Session.EventCode.SessionAuthenticationFailed,
        ]:
            _cb = self._on_state_cb
        elif event_code not in [
            self.EventCode.DataRequestOk,
            self.EventCode.StreamConnecting,
            self.EventCode.StreamConnected,
            self.EventCode.StreamDisconnected,
        ]:
            _cb = self._on_event_cb
        return _cb

    ############################
    # methods for HTTP request #
    ############################
    async def _http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        auto_retry = kwargs.pop("auto_retry", False)

        if method is None:
            method = "GET"

        if headers is None:
            headers = {}

        if self._access_token is not None:
            headers["Authorization"] = "Bearer {}".format(self._access_token)

        if closure is not None:
            headers["Closure"] = closure

        headers.update({"x-tr-applicationid": self.app_key})

        #   http request timeout
        if "timeout" not in kwargs:
            #   override using the http request timeout from config file
            http_request_timeout = self.http_request_timeout_secs
            kwargs["timeout"] = http_request_timeout

        self.debug(
            f"Request to {url}\n\tmethod = {method}\n\t"
            f"headers = {headers}\n\tparams = {params}\n\t"
            f"data = {data}\n\tjson = {json}"
        )

        if auto_retry:
            # if auto retry is True, use self._http_session_auto_retry_client to send request
            _http_request = requests_async.Request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                json=json,
            ).prepare()
            try:
                request_response = await self._http_session_auto_retry_client.send(
                    _http_request, **kwargs
                )

            except urllib3.exceptions.MaxRetryError as error:
                self.error(error)
                raise error

            except (
                requests_async.exceptions.RequestException,
                requests_async.exceptions.HTTPError,
                requests_async.exceptions.ConnectionError,
                requests_async.exceptions.TooManyRedirects,
                requests_async.exceptions.ConnectTimeout,
                requests_async.exceptions.FileModeWarning,
                requests_async.exceptions.ReadTimeout,
                requests_async.exceptions.Timeout,
                requests_async.exceptions.URLRequired,
            ) as error:
                self.error(
                    f"An error occurred while requesting {error.request.url!r}.\n\t{error!r}"
                )
                raise error
        else:
            # without auto_retry, use self._httpx_async_client to send request
            _http_request = httpx.Request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                json=json,
            )

            try:
                request_response = await self._httpx_async_client.send(
                    _http_request, **kwargs
                )
            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.HTTPStatusError,
                httpx.InvalidURL,
                httpx.LocalProtocolError,
                httpx.NetworkError,
                httpx.ProtocolError,
                httpx.ProxyError,
                httpx.ReadError,
                httpx.RequestError,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError,
                httpx.TooManyRedirects,
                httpx.TransportError,
                httpx.TimeoutException,
            ) as error:
                self.error(
                    f"An error occurred while requesting {error.request.url!r}.\n\t{error!r}"
                )
                raise error

        assert request_response is not None
        self.debug(
            f"HTTP request response {request_response.status_code}: {request_response.text}"
        )
        return request_response

    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await self._http_request_async(
            url=url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )

    def http_request(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        headers = headers or {}
        loop = loop or self._loop
        response = loop.run_until_complete(
            self.http_request_async(
                url=url,
                method=method,
                headers=headers,
                data=data,
                params=params,
                json=json,
                closure=closure,
                auth=auth,
                loop=loop,
                **kwargs,
            )
        )
        return response


EventCode = Session.EventCode
