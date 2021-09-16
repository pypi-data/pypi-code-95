# coding: utf-8

__all__ = ["DesktopSession"]

import logging
import socket

import httpx
from appdirs import *

from ._session import Session
from ._session_cxn_type import SessionCxnType
from ._session_state import SessionState
from ._session_type import SessionType
from ... import __version__, DesktopSessionError
from ...tools._common import urljoin


def _update_port_in_url(url, port):
    try:
        protocol, path, default_port = url.split(":")
    except ValueError:
        protocol, path, *_ = url.split(":")

    if port is not None:
        retval = ":".join([protocol, path, str(port)])
    else:
        retval = url

    return retval


class DesktopSession(Session):
    type = SessionType.DESKTOP

    class Params(Session.Params):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def __init__(
        self,
        app_key,
        on_state=None,
        on_event=None,
        session_name="default-session",
        base_url=None,
        platform_path_rdp=None,
        platform_path_udf=None,
        handshake_url=None,
        token=None,
        dacs_position=None,
        dacs_application_id=None,
    ):

        super().__init__(
            app_key=app_key,
            on_state=on_state,
            on_event=on_event,
            token=token,
            dacs_position=dacs_position,
            dacs_application_id=dacs_application_id,
            session_name=session_name,
        )

        self._port = None
        self._udf_url = None
        self._timeout = self.http_request_timeout_secs
        self._user = "root"
        self._check_port_result = False

        self._base_url = base_url
        self._platform_path_rdp = platform_path_rdp
        self._platform_path_udf = platform_path_udf
        self._handshake_url = handshake_url
        #   a mapping the stream connection status
        self._stream_connection_name_to_status = {}

        self._logger.debug(
            "".join(
                [
                    f"DesktopSession created with following parameters:",
                    f' app_key="{app_key}", session_name="{session_name}"',
                    f' base_url="{base_url}"' if base_url is not None else "",
                    f' platform_path_rdp="{platform_path_rdp}"'
                    if platform_path_rdp
                    else "",
                    f' platform_path_udf="{platform_path_udf}"'
                    if platform_path_udf
                    else "",
                    f' handshake_url="{handshake_url}"' if handshake_url else "",
                ]
            )
        )

    def _get_session_cxn_type(self) -> SessionCxnType:
        return SessionCxnType.DESKTOP

    def _get_udf_url(self):
        """
        Returns the scripting proxy url.
        """
        return self._udf_url

    def _get_handshake_url(self, port=None):
        port = port or self._port
        url = _update_port_in_url(self._base_url, port)
        url = urljoin(url, self._handshake_url)
        return url

    def _get_base_url(self, port=None):
        port = port or self._port
        url = _update_port_in_url(self._base_url, port)
        return url

    def _get_rdp_url_root(self):
        if self._platform_path_rdp is None:
            raise ValueError(
                f"Can't find '{self.name}.platform-paths.rdp' "
                f"in config file. Please add this attribute."
            )

        url = _update_port_in_url(self._base_url, self._port)
        url = urljoin(url, self._platform_path_rdp)
        return url

    def set_timeout(self, timeout):
        """
        Set the timeout for requests.
        """
        self._timeout = timeout

    def get_timeout(self):
        """
        Returns the timeout for requests.
        """
        return self._timeout

    def set_port_number(self, port_number, logger=None):
        """
        Set the port number to reach Desktop API proxy.
        """
        self._port = port_number
        if port_number:
            try:
                protocol, path, default_port = self._base_url.split(":")
            except ValueError:
                protocol, path, *_ = self._base_url.split(":")
                default_port = ""

            if self._platform_path_udf is None:
                raise ValueError(
                    f"Can't find '{self.name}.platform-paths.udf'"
                    f" in config file. Please add this attribute."
                )

            try:
                url = ":".join([protocol, path, str(self._port)])
            except TypeError:
                url = ":".join([protocol, path, default_port])

            self._udf_url = urljoin(url, self._platform_path_udf)
            self.close()
        else:
            self._udf_url = None

        if logger:
            logger.info(f"Set Proxy port number to {self._port}")

    def get_port_number(self):
        """
        Returns the port number
        """
        return self._port

    def is_session_logged(self, name: str = None):
        """note that currently the desktop session support only 1 websocket connection"""
        name = name or "pricing"
        assert name in self._stream_connection_name_to_stream_connection_dict
        return self._stream_connection_name_to_stream_connection_dict[name].ready.done()

    ############################################################
    #   multi-websockets support

    def _get_stream_status(self, stream_connection_name: str) -> enumerate:
        """this method is designed for getting a status of given stream service.

        Parameters
        ----------
            a enum of stream service
        Returns
        -------
        enum
            status of stream service.
        """
        return self._stream_connection_name_to_status.get(stream_connection_name)

    def _set_stream_status(
        self, stream_connection_name: str, stream_status: enumerate
    ) -> None:
        """set status of given stream service

        Parameters
        ----------
        streaming_connection
            a service name of stream
        stream_status
            a status enum of stream
        Returns
        -------
        None
        """
        self._stream_connection_name_to_status[stream_connection_name] = stream_status

    def get_omm_login_message_key_data(self):
        """return the login message for OMM 'key' section"""
        return {
            "Elements": {
                "AppKey": self.app_key,
                "ApplicationId": self._dacs_params.dacs_application_id,
                "Position": self._dacs_params.dacs_position,
            }
        }

    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP"""
        return {
            "method": "Auth",
            "streamID": f"{stream_id:d}",
            "appKey": self.app_key,
        }

    #######################################
    #  methods to open and close session  #
    #######################################
    def open(self):
        if self._state in [SessionState.Pending, SessionState.Open]:
            # session is already opened or is opening
            return self._state

        # call Session.open() based on open_async() => _init_streaming_config will be called later
        return super(DesktopSession, self).open()

    ############################################
    #  methods to open asynchronously session  #
    ############################################
    async def open_async(self):
        def close_state(msg):
            self._state = SessionState.Closed
            self._on_event(Session.EventCode.SessionAuthenticationFailed, msg)
            self._on_state(self._state, "Session is closed.")

        if self._state in [SessionState.Pending, SessionState.Open]:
            # session is already opened or is opening
            return self._state

        error = None
        port_number = await self.identify_scripting_proxy_port()

        if port_number:
            try:
                await self.handshake(port_number)
            except DesktopSessionError as e:
                self.error(e.message)
                error = e

            if not error:
                self.set_port_number(port_number)
                self.info(f"Application ID: {self.app_key}")
                self._state = SessionState.Open
                self._on_state(self._state, "Session is opened.")

        not port_number and close_state("Eikon is not running")
        error and close_state(error.message)
        await super(DesktopSession, self).open_async()
        return self._state

    @staticmethod
    def read_firstline_in_file(filename, logger=None):
        try:
            f = open(filename)
            first_line = f.readline()
            f.close()
            return first_line
        except IOError as e:
            if logger:
                logger.error(f"I/O error({e.errno}): {e.strerror}")
            return ""

    async def identify_scripting_proxy_port(self):
        """
        Returns the port used by the Scripting Proxy stored in a configuration file.
        """
        import platform
        import os

        port = None
        path = []
        app_names = ["Data API Proxy", "Eikon API proxy", "Eikon Scripting Proxy"]
        for app_author in ["Refinitiv", "Thomson Reuters"]:
            if platform.system() == "Linux":
                path = path + [
                    user_config_dir(app_name, app_author, roaming=True)
                    for app_name in app_names
                    if os.path.isdir(
                        user_config_dir(app_name, app_author, roaming=True)
                    )
                ]
            else:
                path = path + [
                    user_data_dir(app_name, app_author, roaming=True)
                    for app_name in app_names
                    if os.path.isdir(user_data_dir(app_name, app_author, roaming=True))
                ]

        if len(path):
            port_in_use_file = os.path.join(path[0], ".portInUse")

            # Test if ".portInUse" file exists
            if os.path.exists(port_in_use_file):
                # First test to read .portInUse file
                firstline = self.read_firstline_in_file(port_in_use_file)
                if firstline != "":
                    saved_port = firstline.strip()
                    await self.check_port(saved_port)
                    if self._check_port_result:
                        port = saved_port
                        self.info(f"Port {port} was retrieved from .portInUse file")

        if port is None:
            self.info(
                "Warning: file .portInUse was not found. Try to fallback to default port number."
            )
            port_list = ["9000", "36036"]
            for port_number in port_list:
                self.info(f"Try defaulting to port {port_number}...")
                await self.check_port(port_number)
                if self._check_port_result:
                    return port_number

        if port is None:
            self.error(
                "Error: no proxy address identified.\nCheck if Desktop is running."
            )
            return None

        return port

    async def check_port(self, port, timeout=None):

        #   set default timeout
        timeout = timeout if timeout is not None else self._timeout

        url = f"http://127.0.0.1:{port}/api/status"
        try:
            response = await self._http_request_async(
                url=url,
                method="GET",
                # headers=_headers,
                # json=body,
                timeout=timeout,
            )

            self.info(
                f"Checking port {port} response : {response.status_code} - {response.text}"
            )
            self._check_port_result = True
            return
        except (socket.timeout, httpx.ConnectTimeout):
            self.log(logging.INFO, f"Timeout on checking port {port}")
        except ConnectionError as e:
            self.log(logging.INFO, f"Connexion Error on checking port {port} : {e!r}")
        except Exception as e:
            self.debug(f"Error on checking port {port} : {e!r}")
        self._check_port_result = False

    async def handshake(self, port, timeout=None):
        #   set default timeout
        timeout = timeout if timeout is not None else self._timeout

        url = self._get_handshake_url(port)
        self.info(f"Try to handshake on url {url}...")
        try:
            # DAPI for E4 - API Proxy - Handshake
            _body = {
                "AppKey": self.app_key,
                "AppScope": "trapi",
                "ApiVersion": "1",
                "LibraryName": "RDP Python Library",
                "LibraryVersion": __version__,
            }

            _headers = {"Content-Type": "application/json"}

            response = None
            try:
                response = await self._http_request_async(
                    url=url,
                    method="POST",
                    headers=_headers,
                    json=_body,
                    timeout=timeout,
                )

                self.info(f"Response : {response.status_code} - {response.text}")
            except Exception as e:
                self.log(1, f"HTTP request failed: {e!r}")

            if response:
                if response.status_code == httpx.codes.OK:
                    result = response.json()
                    self._access_token = result.get("access_token")
                elif response.status_code == httpx.codes.BAD_REQUEST:
                    self.error(
                        f"Status code {response.status_code}: "
                        f"Bad request on handshake port {port} : {response.text}"
                    )
                    key_is_incorrect_msg = (
                        f"Status code {response.status_code}: App key is incorrect"
                    )
                    self._on_event(
                        Session.EventCode.SessionAuthenticationFailed,
                        key_is_incorrect_msg,
                    )
                    raise DesktopSessionError(1, key_is_incorrect_msg)
                else:
                    self.debug(
                        f"Response {response.status_code} on handshake port {port} : {response.text}"
                    )

        except (socket.timeout, httpx.ConnectTimeout):
            raise DesktopSessionError(1, f"Timeout on handshake port {port}")
        except Exception as e:
            raise DesktopSessionError(1, f"Error on handshake port {port} : {e!r}")
        except DesktopSessionError as e:
            raise e
