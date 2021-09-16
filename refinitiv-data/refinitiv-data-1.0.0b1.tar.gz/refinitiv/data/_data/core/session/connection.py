import abc
import logging
import sys
import urllib.parse

from ._session import Session
from .authentication_token_handler_thread import AuthenticationTokenHandlerThread
from .stream_service_discovery.stream_connection_configuration import (
    RealtimeDistributionSystemConnectionConfiguration,
    DesktopStreamConnectionConfiguration,
)
from .stream_service_discovery.stream_service_discovery_handler import (
    StreamServiceInformation,
    PlatformStreamServiceDiscoveryHandler,
    DesktopStreamServiceDiscoveryHandler,
)
from ... import configure
from ...errors import PlatformSessionError


class SessionConnection(abc.ABC):
    def __init__(self, session):
        self._session = session

        self.log = session.log
        self.debug = session.debug

    @abc.abstractmethod
    async def get_stream_connection_configuration(self, stream_connection_name: str):
        pass


class PlatformConnection(SessionConnection, abc.ABC):
    def __init__(self, session):
        super().__init__(session)
        self.streaming_connection_name_and_connection_type_to_status = {}

    @abc.abstractmethod
    def get_omm_login_message_key_data(self):
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    async def waiting_for_stream_ready(self, open_state):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def authorize(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    def get_stream_status(self, streaming_connection_name):
        return self.streaming_connection_name_and_connection_type_to_status.get(
            streaming_connection_name, Session.EventCode.StreamDisconnected
        )

    def set_stream_status(self, streaming_connection_name, stream_status):
        self.streaming_connection_name_and_connection_type_to_status[
            streaming_connection_name
        ] = stream_status


class RefinitivDataConnection(PlatformConnection):
    def __init__(self, session):
        super().__init__(session)

        #   authentication token handler
        self._authentication_token_handler_thread = None

    def get_omm_login_message_key_data(self):
        return {
            "NameType": "AuthnToken",
            "Elements": {
                "AuthenticationToken": self._session._access_token,
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

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
        return await self._session._http_request_async(
            url,
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

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """

        #   two ways of specific stream connection are discovery endpoint and WebSocket URL

        #       WebSocket url
        streaming_connection_endpoint_websocket_url = (
            self._session.get_streaming_websocket_endpoint_url(stream_connection_name)
        )
        #       discovery endpoint
        streaming_connection_discovery_endpoint_url = (
            self._session.get_streaming_discovery_endpoint_url(stream_connection_name)
        )

        #       protocols
        streaming_connection_supported_protocols = (
            self._session.get_streaming_protocols(stream_connection_name)
        )
        self._session.debug(
            f"          {stream_connection_name} supported protocol are {streaming_connection_supported_protocols}"
        )

        #   check for valid path for stream discovery endpoint
        if streaming_connection_endpoint_websocket_url is not None:
            #   override discovery endpoint by specific WebSocket endpoint url
            self._session.debug(
                f"override streaming by WebSocket endpoint url : {streaming_connection_endpoint_websocket_url}"
            )

            #   build the stream service information and stream connection configuration

            #       parse the WebSocket url and build stream service information
            websocket_url_parse = urllib.parse.urlparse(
                streaming_connection_endpoint_websocket_url
            )
            stream_service_information = StreamServiceInformation(
                scheme=websocket_url_parse.scheme,
                host=websocket_url_parse.hostname,
                port=websocket_url_parse.port,
                path=websocket_url_parse.path.lstrip("/"),
                data_formats=["unknown"],
                location=None,
            )

            #   build the stream connection configuration
            return RealtimeDistributionSystemConnectionConfiguration(
                self._session,
                [
                    stream_service_information,
                ],
                streaming_connection_supported_protocols,
            )

        elif streaming_connection_discovery_endpoint_url is not None:
            #   valid stream discovery endpoint url
            self.debug(
                f"using discovery endpoint url : {streaming_connection_discovery_endpoint_url}"
            )

            #   get the location specific from config file
            #       get the stream connection name
            streaming, streaming_name, endpoint_name = stream_connection_name.split("/")
            assert streaming == "streaming"

            #   build the streaming connection config string
            streaming_connection_endpoint_location_name = (
                f"apis.streaming.{streaming_name}.endpoints.{endpoint_name}.locations"
            )
            try:
                prefer_stream_service_locations = configure.config.get_list(
                    streaming_connection_endpoint_location_name
                )
            except KeyError:
                prefer_stream_service_locations = []

            #   request the WebSocket endpoint from discovery service
            service_discovery_handler = PlatformStreamServiceDiscoveryHandler(
                self._session,
                streaming_connection_discovery_endpoint_url,
                prefer_stream_service_locations=prefer_stream_service_locations,
            )
            stream_service_information = (
                await service_discovery_handler.get_stream_service_information()
            )

            #   build the stream connection configuration
            return RealtimeDistributionSystemConnectionConfiguration(
                self._session,
                stream_service_information,
                streaming_connection_supported_protocols,
            )

        else:
            #   error
            raise ValueError(
                "ERROR!!! streaming connection needed by specific url and path in endpoint section or specific WebSocket url."
            )

    async def waiting_for_stream_ready(self, open_state):
        pass

    def _initialize_authentication_handler_thread(self):
        self._authentication_token_handler_thread = AuthenticationTokenHandlerThread(
            self._session,
            self._session._grant,
            self._session.authentication_token_endpoint_url,
            server_mode=self._session.server_mode,
        )

    def open(self):
        #   build the token handler for this platform session
        self._initialize_authentication_handler_thread()

        #   call authorize for do an authentication mechanism to the RDP platform by another thread
        self.authorize()

    def authorize(self):
        """do an authentication by calling a method in AuthenticationTokenHandlerThread."""

        #   do authentication until successful when the server mode is enable
        while True:

            #   request a authentication token and wait for it
            is_authorize_failed = False
            try:
                self._authentication_token_handler_thread.authorize()
            except Exception as e:
                #   error occur when request an authorization

                #   check the sever-mode is enabled or not?
                if not self._session.server_mode:
                    #   do nothing because the server-mode is disabled
                    self._session.error(
                        f"ERROR!!! failed to request an authorization to platfrom.\n"
                        f"Unexpected error {sys.exc_info()[0]}.\n"
                        "(auto-reconnection is disabled)"
                    )

                    raise PlatformSessionError(
                        -1,
                        "ERROR!!! Authentication handler failed to request a access token.\n"
                        f"{sys.exc_info()[0]}.",
                    )

                else:
                    #   retry again
                    self._session.warning(
                        "WARNING!!! retring after failed to request an authorization to platfrom.\n"
                        f"Unexpected error {sys.exc_info()[0]}.\n"
                        "(auto-reconnection is enabled)"
                    )
                    is_authorize_failed = True

            self._session.debug(
                f"               waiting for authorize is ready.........."
            )
            self._authentication_token_handler_thread.wait_for_authorize_ready()

            #   check the request a new authentication success or not?
            if (
                is_authorize_failed
                or self._authentication_token_handler_thread.is_error()
            ):
                #   failed to request an authorized in the thread loop
                if not self._session.server_mode:
                    #   do nothing because the server-mode is disabled
                    self._session.error(
                        "ERROR!!! CANNOT authorize to RDP authentication endpoint.\n"
                        f"Unexpected error {self._authentication_token_handler_thread.last_exception}.\n"
                        "(auto-reconnection is disabled)"
                    )

                    #   raise the error
                    raise PlatformSessionError(
                        -1,
                        "ERROR!!! Authentication handler failed to request a access token.\n"
                        f"{self._authentication_token_handler_thread.last_exception}",
                    )

                else:
                    self._session.warning(
                        "WARNING!!! retrying after authentication token thread failed.\n"
                        f"Unexpected error {self._authentication_token_handler_thread.last_exception}."
                    )

                    #   stop and close the current authentication handler thread
                    try:
                        self._authentication_token_handler_thread.stop()
                    except:
                        #   possible the authentication token handler thread cannot stop properly
                        self._session.warning(
                            "WARNING!!! CANNOT properly stop authentication token handler thread .\n"
                            f"Unexpected error {sys.exc_info()[0]}."
                        )

                    #   re-initialize the authentication handler
                    self._initialize_authentication_handler_thread()

            else:
                #   successfully request an authorization
                self._session.debug(
                    "Successfully request an authorization by authentication token handler thread."
                )
                break

    def close(self):
        self.log(logging.DEBUG, "Close platform session...")
        self._authentication_token_handler_thread and self._authentication_token_handler_thread.stop()
        return super().close()


class DeployedConnection(PlatformConnection):
    """this class is designed for a connection to the realtime distribution system (aka. deployed platform or TREP)"""

    def __init__(self, session):
        super().__init__(session)
        self.streaming_connection_name_and_connection_type_to_status[
            self._session._deployed_platform_connection_name
        ] = Session.EventCode.StreamDisconnected

    def get_omm_login_message_key_data(self):
        return {
            "Name": self._session._dacs_params.deployed_platform_username,
            "Elements": {
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

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
        raise PlatformSessionError(
            -1,
            "Error!!! Platform session cannot connect to refinitiv dataplatform. "
            "Please check or provide the access right.",
        )

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """
        assert stream_connection_name.startswith("streaming/pricing")

        #   get the realtime distribution system information from config file
        if self._session._deployed_platform_host is None:
            #   read from config file.
            realtime_distribution_system_url_key = f"{configure.keys.platform_realtime_distribution_system(self._session.name)}.url"
            realtime_distribution_system_url = configure.get_str(
                realtime_distribution_system_url_key
            )
            self._session.debug(
                f"using the Refinitiv realtime url at {realtime_distribution_system_url}"
            )

            #   construct host for host name and port
            realtime_distribution_system_url_parse = urllib.parse.urlparse(
                realtime_distribution_system_url
            )
            self._session.debug(
                f"      realtime_distribution_system scheme   = {realtime_distribution_system_url_parse.scheme}"
            )
            self._session.debug(
                f"      realtime_distribution_system endpoint = {realtime_distribution_system_url_parse.hostname}"
            )
            self._session.debug(
                f"      realtime_distribution_system port     = {realtime_distribution_system_url_parse.port}"
            )

            #   build the StreamServiceInformation
            stream_service_information = StreamServiceInformation(
                scheme=realtime_distribution_system_url_parse.scheme,
                host=realtime_distribution_system_url_parse.hostname,
                port=realtime_distribution_system_url_parse.port,
                path=None,
                data_formats=["tr_json2"],
                location=None,
            )
        else:
            #   use the hostname and port parameter from session
            (
                deployed_platform_hostname,
                deployed_platform_port,
            ) = self._session._deployed_platform_host.split(":")

            #   build the StreamServiceInformation
            stream_service_information = StreamServiceInformation(
                scheme="ws",
                host=deployed_platform_hostname,
                port=deployed_platform_port,
                path=None,
                data_formats=["tr_json2"],
                location=None,
            )

        #   build the stream connection configuration
        #       note it has only one realtime distribution.
        return RealtimeDistributionSystemConnectionConfiguration(
            self._session,
            [
                stream_service_information,
            ],
            [
                "OMM",
            ],
        )

    async def waiting_for_stream_ready(self, open_state):
        self.debug("waiting for deployed platform streaming ready.")

        #   do waiting for deployed platform session
        await self._session.wait_for_streaming(
            "streaming/pricing/main", "OMM"
        ) and open_state()

    def open(self):
        super().open()

    def authorize(self):
        pass

    def close(self):
        self.log(logging.DEBUG, "Close platform session...")
        super().close()


class RefinitivDataAndDeployedConnection(DeployedConnection, RefinitivDataConnection):
    def __init__(self, session):
        DeployedConnection.__init__(self, session)
        RefinitivDataConnection.__init__(self, session)

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
        return await RefinitivDataConnection.http_request_async(
            self,
            url,
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

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """

        #   check this is streaming/pricing or not?
        if stream_connection_name.startswith("streaming/pricing/main"):
            #   using the realtime distribution system
            return await DeployedConnection.get_stream_connection_configuration(
                self, stream_connection_name
            )
        else:
            #   using the platform streaming
            return await RefinitivDataConnection.get_stream_connection_configuration(
                self, stream_connection_name
            )

    def open(self):
        RefinitivDataConnection.open(self)

    def authorize(self):
        RefinitivDataConnection.authorize(self)

    def close(self):
        RefinitivDataConnection.close(self)


class DesktopConnection(SessionConnection):
    async def get_stream_connection_configuration(self, stream_connection_name: str):
        streaming_connection_discovery_endpoint_url = (
            self._session.get_streaming_discovery_endpoint_url(stream_connection_name)
        )

        streaming_connection_endpoint_websocket_url = (
            self._session.get_streaming_websocket_endpoint_url(stream_connection_name)
        )

        streaming_connection_supported_protocols = (
            self._session.get_streaming_protocols(stream_connection_name)
        )

        self._session.debug(
            f"          {stream_connection_name} supported protocol are "
            f"{streaming_connection_supported_protocols}"
        )

        if streaming_connection_endpoint_websocket_url is not None:

            self._session.debug(
                f"\nOverride streaming by WebSocket endpoint url : "
                f"{streaming_connection_endpoint_websocket_url}\n"
            )

            websocket = urllib.parse.urlparse(
                streaming_connection_endpoint_websocket_url
            )

            base_session_url = urllib.parse.urlparse(self._session._base_url)

            if websocket.netloc != base_session_url.netloc:
                raise ValueError(
                    f"Missmatch between websocket url and base session url\n"
                    f"{websocket.netloc} != {base_session_url.netloc}"
                )

            stream_service_information = [
                StreamServiceInformation(
                    scheme=websocket.scheme,
                    host=websocket.hostname,
                    port=websocket.port,
                    path=websocket.path.lstrip("/"),
                    data_formats=["unknown"],
                    location=None,
                )
            ]

        elif streaming_connection_discovery_endpoint_url is not None:

            service_discovery_handler = DesktopStreamServiceDiscoveryHandler(
                self._session, streaming_connection_discovery_endpoint_url
            )
            stream_service_information = (
                await service_discovery_handler.get_stream_service_information()
            )
        else:
            raise ValueError(
                "ERROR!!! streaming connection needed by specific url"
                " and path in endpoint section or specific WebSocket url."
            )

        stream_connection_configuration = DesktopStreamConnectionConfiguration(
            self._session,
            stream_service_information,
            streaming_connection_supported_protocols,
        )

        return stream_connection_configuration
