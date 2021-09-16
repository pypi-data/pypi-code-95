# coding: utf-8

__all__ = ["PlatformSession"]

import urllib.parse

from ._session import Session
from ._session_cxn_type import SessionCxnType
from ._session_state import SessionState
from ._session_type import SessionType
from .grant import Grant
from .grant_password import GrantPassword
from ...tools._common import urljoin


class PlatformSession(Session):
    """This class is designed for handling the session to Refinitiv Data Platform (RDP) or Deployed Platform (TREP)
    - Refinitiv Data Platform are including handling an authentication and a token management (including refreshing token),
        also handling a real-time service discovery to get the service websocket endpoint
        and initialize the login for streaming
    - Deployed Platform is including the login for streaming
    """

    type = SessionType.PLATFORM

    class Params(Session.Params):
        def __init__(self, *args, **kwargs):
            super(PlatformSession.Params, self).__init__(*args, **kwargs)

            self._grant = kwargs.get("grant")
            _signon_control = kwargs.get("signon_control", "False")
            self._take_signon_control = _signon_control.lower() == "true"

            if self._take_signon_control is None:
                self._take_signon_control = False

            #   for deployed platform connection
            self._deployed_platform_host = kwargs.get("deployed_platform_host")

        def get_grant(self):
            return self._grant

        def grant_type(self, grant):
            if isinstance(grant, Grant):
                self._grant = grant
            else:
                raise Exception("wrong Elektron authentication parameter")
            return self

        def take_signon_control(self):
            return self._take_signon_control

        def with_take_signon_control(self, value):
            if value is not None:
                self._take_signon_control = value
            return self

        #   for deployed platform connection
        def deployed_platform_host(self, deployed_platform_host):
            self._deployed_platform_host = deployed_platform_host
            return self

        def with_authentication_token(self, token):
            if token:
                self._dacs_params.authentication_token = token
            return self

    def get_session_params(self):
        return self._session_params

    def session_params(self, session_params):
        self._session_params = session_params
        return session_params

    def _get_rdp_url_root(self):
        return self._base_url

    def __init__(
        self,
        app_key=None,
        # for Refinitiv data connection
        grant=None,
        signon_control=None,
        # for Deployed platform connection
        deployed_platform_host=None,
        authentication_token=None,
        deployed_platform_username=None,
        dacs_position=None,
        dacs_application_id=None,
        on_state=None,
        on_event=None,
        session_name="default-session",
        auto_reconnect=None,
        server_mode=None,
        base_url=None,
        auth_url=None,
        auth_authorize=None,
        auth_token=None,
        realtime_distribution_system_url=None,
    ):
        super().__init__(
            app_key,
            on_state=on_state,
            on_event=on_event,
            deployed_platform_username=deployed_platform_username,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
            session_name=session_name,
        )

        self._ws_endpoints = []

        if grant and isinstance(grant, GrantPassword):
            self._grant = grant

        self._take_signon_control = signon_control if signon_control else True

        self._pending_stream_queue = []
        self._pending_data_queue = []

        self._auto_reconnect = auto_reconnect
        self._server_mode = server_mode
        self._base_url = base_url
        self._auth_url = auth_url
        self._auth_authorize = auth_authorize
        self._auth_token = auth_token
        self._realtime_distribution_system_url = realtime_distribution_system_url

        self._access_token = None
        self._token_expires_in_secs = 0
        self._token_expires_at = 0

        self._websocket_endpoint = None

        self._deployed_platform_host = deployed_platform_host
        self._deployed_platform_connection_name = self.name

        self._initialize_realtime_distribution_system_config()

        self._logger.debug(
            f"PlatformSession created with following parameters:"
            f' app_key="{app_key}", session_name="{session_name}"'
        )

    def _get_session_cxn_type(self) -> SessionCxnType:
        if self._grant is not None and self._deployed_platform_host:
            self.debug(
                "Connecting to Refinitiv Data Platform (RDP) and Deployed Platform ..."
            )
            cxn_type = SessionCxnType.REFINITIV_DATA_AND_DEPLOYED

        elif self._grant is not None:
            self.debug("Connecting to Refinitiv Data Platform (RDP) ...")
            cxn_type = SessionCxnType.REFINITIV_DATA

        elif self._deployed_platform_host:
            self.debug("Connecting to realtime distribution system ...")
            cxn_type = SessionCxnType.DEPLOYED

        else:
            raise AttributeError(f"Error!!! Can't initialize a PlatformSession")

        return cxn_type

    ############################################################
    #   reconnection configuration

    @property
    def stream_auto_reconnection(self):
        return self._auto_reconnect

    @property
    def server_mode(self):
        return self._server_mode

    ############################################################
    #   session configuration

    @property
    def authentication_token_endpoint_url(self):
        #   build authentication token url
        authentication_token_endpoint_url = urljoin(
            urljoin(self._get_rdp_url_root(), self._auth_url), self._auth_token
        )
        self.debug(
            f"authentication_token_endpoint_url : {authentication_token_endpoint_url}"
        )

        #   done
        return authentication_token_endpoint_url

    def _get_auth_token_uri(self):
        auth_token_uri = urljoin(self._auth_url, self._auth_token)
        uri = urljoin(self._get_rdp_url_root(), auth_token_uri)
        return uri

    def _initialize_realtime_distribution_system_config(self):
        """check for an initialize the realtime distribution system from config file if the user specific the deployed platform host"""

        #   check the user override the deployed platform (aka TREP) or not?
        if (
            self._deployed_platform_host is None
            and self._realtime_distribution_system_url
        ):
            self.debug(
                f"using the Refinitiv realtime distribution system : url at {self._realtime_distribution_system_url}"
            )
            #   construct host for host name and port
            self._deployed_platform_host = urllib.parse.urlparse(
                self._realtime_distribution_system_url
            ).netloc
            self.debug(f"      deployed_platform_host = {self._deployed_platform_host}")

        else:
            #   using the deployed platform host from user specific
            self.debug(
                f"using the specific deployed platform host : host {self._deployed_platform_host}"
            )

    ############################################################
    #   authentication token

    def request_stream_authentication_token(self):
        """Request new stream authentication token"""
        self.debug(f"{self.__class__.__name__}.request_stream_authentication_token()")
        self._connection.authorize()

    ############################################################
    #   multi-websockets support

    def _get_stream_status(self, stream_connection_name: str) -> enumerate:
        """this method is designed for getting a status of given streaming connection.

        Parameters
        ----------
            a connection string of stream
        Returns
        -------
        enum
            status of stream service.
        """
        return self._connection.get_stream_status(stream_connection_name)

    def _set_stream_status(
        self, stream_connection_name: str, stream_status: enumerate
    ) -> None:
        """set status of given streaming connection

        Parameters
        ----------
        string
            a connection string of stream
        enum
            a status enum of stream
        Returns
        -------
        None
        """
        self._connection.set_stream_status(stream_connection_name, stream_status)

    #################################################
    #   OMM and RDP login message for each kind of session ie. desktop, platform or deployed platform

    def get_omm_login_message_key_data(self):
        """Return the login message for OMM 'key' section"""
        return self._connection.get_omm_login_message_key_data()

    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP"""
        return {
            "streamID": f"{stream_id:d}",
            "method": "Auth",
            "token": self._access_token,
        }

    #######################################
    #  methods to open and close session  #
    #######################################

    def close(self):
        """Close all connection from both Refinitiv Data Platform and Deployed Platform (TREP)"""
        self._connection.close()

        #   call parent for class
        Session.close(self)

    ############################################
    #  methods to open asynchronously session  #
    ############################################
    async def open_async(self):
        def open_state():
            self._state = SessionState.Open
            self._on_state(self._state, "Session is opened.")

        if self._state in [SessionState.Pending, SessionState.Open]:
            # session is already opened or is opening
            return self._state

        #   do authentication process with Refinitiv Data Platform (RDP), if it's necessary
        self._connection.open()

        #   the platform session is ready,
        open_state()

        #   call parent call open_async
        await super(PlatformSession, self).open_async()

        #   waiting for everything ready
        await self._connection.waiting_for_stream_ready(open_state)

        #   done, return state
        return self._state

    ############################
    # methods for HTTP request #
    ############################
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
        return await self._connection.http_request_async(
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
