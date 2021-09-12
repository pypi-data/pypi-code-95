import logging

import requests
from requests import codes

from .const import __version__
from .exceptions import (
    Conflict,
    Forbidden,
    InvalidJSON,
    InvalidRequest,
    NotFound,
    ServerError,
    Unauthorized,
)

log = logging.getLogger(__package__)


def urljoin(base, path):
    if base.endswith("/"):  # pragma: no cover
        base = base[:-1]
    if not path.startswith("/"):  # pragma: no cover
        path = f"/{path}"
    return f"{base}{path}"


class Requestor(object):
    """Requestor provides an interface to HTTP requests."""

    _exceptionMapping = {
        400: InvalidRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
        409: Conflict,
        422: ServerError,
        500: ServerError,
        502: ServerError,
        503: ServerError,
        504: ServerError,
        520: ServerError,
        522: ServerError,
    }
    _successCodes = [200, 201, 202, 204]

    def __init__(self, credmgrUrl, auth, sessionClass, **sessionKwargs):
        """Create an instance of the Requestor class.

        :param str credmgrUrl: Url used to make API requests
        :param auth: An auth tuple or a class that subclasses requests.auth
        :param Session sessionClass: (Optional) A custom session class to handle
            requests, compatible with requests.Session(). (Default: None)

        """
        self._baseUrl = credmgrUrl
        self._session = (sessionClass or requests.Session)()
        self._session.auth = auth
        for key, value in sessionKwargs.items():  # pragma: no cover
            setattr(self._session, key, value)
        self._session.headers["User-Agent"] = f"credmgr/{__version__}"

    def __getattr__(self, attribute):  # pragma: no cover
        """Pass all undefined attributes to the _session attribute."""
        if attribute.startswith("__"):
            raise AttributeError
        return getattr(self._session, attribute)

    @staticmethod
    def _logRequest(data, method, params, url):
        log.info(f"Data: {data}")
        log.info(f"Request: {method} {url}")
        log.info(f"Query Parameters: {params}")

    def request(self, path, method, data=None, params=None, **kwargs):
        url = urljoin(self._baseUrl, path)
        self._logRequest(data, method, params, url)
        response = self._session.request(method, url, params, data=data, **kwargs)
        if response.status_code in self._exceptionMapping:
            raise self._exceptionMapping[response.status_code](response)
        elif response.status_code == codes["no_content"]:
            return
        assert (
            response.status_code in self._successCodes
        ), f"Unexpected status code: {response.status_code}"
        if response.headers.get("content-length") == "0":  # pragma: no cover
            return ""
        try:
            response.json()
        except ValueError:  # pragma: no cover
            raise InvalidJSON(response)
        log.info(
            f'Response: {response.status_code} ({response.headers.get("content-length")} bytes)'
        )
        return response
