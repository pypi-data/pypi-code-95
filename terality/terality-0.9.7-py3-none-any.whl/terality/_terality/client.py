from __future__ import annotations

from common_client_scheduler.exceptions import TeralityError
from terality._terality.utils.config import TeralityConfig, TeralityCredentials
from typing import Any, Optional

from common_client_scheduler.config import SessionInfo
from common_client_scheduler.requests_responses import (
    CreateSessionResponse,
    PendingComputationResponse,
)
from .httptransport import AuthCredentials, HttpTransport
from .utils import logger


class UnconfiguredTeralityClientError(TeralityError):
    pass


class SessionStateError(TeralityError):
    pass


class TeralityClient:
    """Implement the connectivity with the Terality API.

    This is a stateful class managing authentication and session management. Currently, a single client
    may only have one session active at any given time.

    This client is not thread-safe.

    The client can be in an "unconfigured state" (no HttpTransport associated to it). In this state,
    it will raise an exception on each request.
    The first time such an unconfigured client is called, it will log a detailed error message.

    Args:
        http_transport: the underlying HttpTransport used to perform requests. If None, then this
            client will raise a user-friendly exception on each request, explaining how to configure Terality.
        auto_session: if True, when no session is currently opened, the TeralityClient will start a new session
            before performing a request.
    """

    # Note: the session management could be split to a separate class, but for now this class
    # is small enough to keep it inline.

    def __init__(self, http_transport: Optional[HttpTransport], auto_session: bool = False) -> None:
        self._http_transport = http_transport
        self._has_printed_error_message = False
        self._session: Optional[SessionInfo] = None
        self._auto_session = auto_session

    def send_request(self, route: str, payload: Optional[Any], method="POST") -> Any:
        """Send a request to the Terality API, injecting credentials and a session ID when relevant.

        The arguments are the same as the `request` method on the underlying HttpTransport.
        """
        self._raise_if_unconfigured()
        assert self._http_transport is not None

        if self._auto_session and self._session is None:
            self.start_session()

        session_id = self._session.id if self._session is not None else None

        return self._http_transport.request(route, payload, session_id=session_id, method=method)

    def poll_for_answer(self, route: str, payload: Any, method="POST"):
        """Same as `send_request`, except that it polls the API on a PendingComputationResponse.

        On long running jobs, the API may answer with a PendingComputationResponse. This methods keeps
        polling the API until the answer is a real result.
        """
        response = self.send_request(route, payload, method=method)
        while isinstance(response, PendingComputationResponse):
            function_id = response.pending_computation_id
            response = self.send_request("follow_up", {"function_id": function_id})
        return response

    def start_session(self):
        """Start a session.

        Before processing data, the client must start a session. The data created during the session is bound
        to the session: when the session is closed, the data is garbage collected. Most API calls that deal
        with data processing require an open session.

        Raise:
            SessionStateError: if a session is already in progress
        """
        if self._session is not None:
            raise SessionStateError("A session is already opened on this client.")

        self._raise_if_unconfigured()
        assert self._http_transport is not None

        session = self._http_transport.request("create_session", payload=None)
        if not isinstance(session, CreateSessionResponse):
            raise RuntimeError(
                f"Unexpected server response type, got {type(session)}, expected SessionInfo."
            )

        self._session = SessionInfo(
            id=session.id,
            upload_config=session.upload_config,
            download_config=session.download_config,
        )

    def get_download_config(self):
        self._raise_if_unconfigured()
        if self._session is None:
            raise SessionStateError(
                "Can not get a download config on a client that does not have an active session."
            )
        return self._session.download_config

    def get_upload_config(self):
        self._raise_if_unconfigured()
        if self._session is None:
            raise SessionStateError(
                "Can not get an upload config on a client that does not have an active session."
            )
        return self._session.upload_config

    def close_session(self):
        """Close the current session, if any.

        If no session is in progress, this method is a no-op.
        """
        self._raise_if_unconfigured()
        if self._session is None:
            return

        assert self._http_transport is not None

        self._http_transport.request("delete_session", None, session_id=self._session.id)
        self._session = None

    def _raise_if_unconfigured(self):
        if self._http_transport is not None:
            return
        if not self._has_printed_error_message:
            self._has_printed_error_message = True
            # TODO: better error message
            logger.warning("Could not read the Terality configuration files.")
        raise UnconfiguredTeralityClientError(
            "The Terality client is not configured (more info at https://docs.terality.com/)"
        )


class UnreadableTeralityConfigError(TeralityError):
    pass


def client_from_config() -> TeralityClient:
    """Try to read the Terality configuration files, and return a configured TeralityClient from them.

    Raise:
        UnreadableTeralityConfigError: if the Terality configuration files are not accessible.

    See:
        unconfigured_client
    """
    try:
        config = TeralityConfig.load()
        credentials = TeralityCredentials.load()
        auth_credentials = AuthCredentials(
            user=credentials.user_id, password=credentials.user_password
        )
        http_transport = HttpTransport(
            base_url=config.full_url(),
            request_timeout=config.timeout,
            auth_credentials=auth_credentials,
        )
        return TeralityClient(http_transport, auto_session=True)
    except Exception as e:
        raise UnreadableTeralityConfigError("could not read Terality configuration files") from e


def unconfigured_client() -> TeralityClient:
    """
    Return an unconfigured TeralityClient. This client will raise an exception on each request.

    Useful when the caller tried to call `client_from_config`, but no config was available. This unconfigured
    client can be used to signal to the user that it needs to configure Terality.
    """
    return TeralityClient(http_transport=None, auto_session=False)


def anonymous_client(api_url: Optional[str] = None) -> TeralityClient:
    """Return an anonymous Terality client (e.g a client that does not authenticate its requests).

    Args:
        api_url: if not provided, try to get the base URL from a configuration file. If the configuration
            file is missing or unreadable, then silently use the default settings embedded in this package.
            This function can thus be safely called even on systems where Terality is not configured yet.
    """
    timeout = (1, 1)
    if api_url is None:
        config = TeralityConfig.load(fallback_to_defaults=True)
        api_url = config.full_url()
        timeout = config.timeout

    http_transport = HttpTransport(base_url=api_url, request_timeout=timeout, auth_credentials=None)
    return TeralityClient(http_transport, auto_session=False)
