import traceback
import urllib.parse
from json import JSONDecodeError

import requests

from ..core.session import get_valid_session
from ..delivery.data.endpoint import RequestMethod, EndpointData
from ..tools._common import urljoin, get_response_reason


# ---------------------------------------------------------------------------
#   Content data
# ---------------------------------------------------------------------------


class Data(EndpointData):
    pass


# ---------------------------------------------------------------------------
#   Response object
# ---------------------------------------------------------------------------

# class Response(EndpointResponse):
class Response:
    def __init__(self, *args, **kwargs):
        self.is_success: bool = kwargs.get("is_success")
        self.data: Data = kwargs.get("content_data")
        self.status = kwargs.get("status")
        self.error_code = kwargs.get("error_code")
        self.error_message = kwargs.get("error_message")
        self._raw_response = kwargs.get("raw_response")
        self.http_response = self._raw_response

    @property
    def headers(self):
        if self._raw_response:
            return self._raw_response.headers
        return None

    @property
    def request_message(self):
        if self._raw_response:
            return self._raw_response.request
        return None

    @property
    def closure(self):
        if self._raw_response:
            request = self._raw_response.request
            headers = request.headers
            return headers.get("closure")
        return None

    @property
    def http_status(self):
        return self.status

    @property
    def http_headers(self):
        return self.headers


# ---------------------------------------------------------------------------
#   Response factory
# ---------------------------------------------------------------------------


class ResponseFactory:
    def __init__(self, response_class=Response, data_class=Data):
        super().__init__()
        self.data_class = data_class
        self.response_class = response_class

    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        inst.data = self.data_class(data.get("content_data"))
        return inst

    def create_fail(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=False, **data)
        inst.data = self.data_class(data.get("content_data"))
        return inst


# ---------------------------------------------------------------------------
#   Request factory
# ---------------------------------------------------------------------------

request_method_value = {
    RequestMethod.POST: "POST",
    RequestMethod.PUT: "PUT",
    RequestMethod.DELETE: "DELETE",
    RequestMethod.GET: "GET",
}


class RequestFactory:
    def get_url(self, *args, **kwargs):
        url = args[1]
        return url

    def create(self, *args, **kwargs):
        session = args[0]
        url = self.get_url(*args, **kwargs)
        url_root = session._get_rdp_url_root()

        method = self.get_request_method(*args, **kwargs)
        header_parameters = kwargs.get("header_parameters") or {}
        path_parameters = self.get_path_parameters(*args, **kwargs)
        query_parameters = self.get_query_parameters(*args, **kwargs)
        extended_params = kwargs.get("extended_params") or {}
        body_parameters = self.get_body_parameters(*args, **kwargs)
        body_parameters.update(extended_params or {})
        closure = kwargs.get("closure")

        url = self.update_url(url_root, url, path_parameters, query_parameters)

        headers = None
        if method != RequestMethod.GET:
            headers = {"Content-Type": "application/json"}
            headers.update(header_parameters)

        request = {
            "url": url,
            "method": request_method_value.get(method),
            "headers": headers,
            "body": body_parameters,
        }

        if closure is not None:
            request["closure"] = closure

        return request

    def update_url(self, url_root, url, path_parameters, query_parameters):
        try:
            result = urllib.parse.urlparse(url)

            if not all([result.scheme, result.netloc, result.path]):
                url = urljoin(url_root, url)

            else:
                url = "".join([url_root, result.path])

        except Exception:
            url = "/".join([url_root + "/" + url])

        if path_parameters:
            for key, value in path_parameters.items():
                value = urllib.parse.quote(value)
                url = url.replace("{" + key + "}", value)

        if query_parameters:
            url = "?".join([url, urllib.parse.urlencode(query_parameters)])

        return url

    def get_request_method(self, *_, **kwargs) -> RequestMethod:
        return kwargs.get("method", RequestMethod.GET)

    def get_body_parameters(self, *_, **kwargs) -> dict:
        return kwargs.get("body_parameters") or {}

    def get_query_parameters(self, *_, **kwargs) -> list:
        return kwargs.get("query_parameters") or []

    def get_path_parameters(self, *_, **kwargs) -> dict:
        return kwargs.get("path_parameters") or {}


# ---------------------------------------------------------------------------
#   Connection object
# ---------------------------------------------------------------------------


class HttpSessionConnection:
    def send(self, request, *args, **kwargs):
        session = args[0]

        if not session.is_open:
            raise ValueError("Session is not opened. Can't send any request")

        method = request.get("method")
        url = request.get("url")
        headers = request.get("headers")
        body = request.get("body")
        auto_retry = kwargs.get("auto_retry", False)
        session.debug(f"Send {method} request to {url}  (auto-retry={auto_retry})")
        session.debug(f"\theaders : {headers}\n\tbody : {body}")
        data = session.http_request(
            url=url,
            method=method,
            headers=headers,
            json=body,
            closure=request.get("closure"),
            auto_retry=auto_retry,
        )
        return data

    async def send_async(self, request, *args, **kwargs):
        session = args[0]

        if not session.is_open:
            raise ValueError("Session is not opened. Can't send any request")

        method = request.get("method")
        url = request.get("url")
        headers = request.get("headers")
        body = request.get("body")
        auto_retry = kwargs.get("auto_retry", False)
        session.debug(
            f"Send {method} request asynchronously to {url}  (auto-retry={auto_retry})"
        )
        session.debug(f"\theaders : {headers}\n\tbody : {body}")
        data = await session.http_request_async(
            url=url,
            method=method,
            headers=headers,
            json=body,
            closure=request.get("closure"),
            auto_retry=auto_retry,
        )
        return data


# ---------------------------------------------------------------------------
#   Raw data parser
# ---------------------------------------------------------------------------


class Parser:
    def process_successful_response(self, raw_response):
        status = {
            "http_status_code": raw_response.status_code,
            "http_reason": get_response_reason(raw_response),
        }

        media_type = raw_response.headers.get("content-type")

        if "/json" in media_type:
            try:
                content_data = raw_response.json()
                if content_data is None:
                    # Some HTTP responses, such as a DELETE,
                    # can be successful without any response body.
                    content_data = {}

                parsed_data = {
                    "status": status,
                    "raw_response": raw_response,
                    "content_data": content_data,
                }
            except (ValueError, TypeError, JSONDecodeError) as error:
                message = f"Failed to process HTTP response : {str(error)}"
                status["content"] = message
                content_data = raw_response.text
                parsed_data = {
                    "status": status,
                    "raw_response": raw_response,
                    "content_data": content_data,
                }

        elif (
            "text/plain" in media_type
            or "text/html" in media_type
            or "text/xml" in media_type
            or "image/" in media_type
        ):
            content_data = raw_response.text
            parsed_data = {
                "status": status,
                "raw_response": raw_response,
                "content_data": content_data,
            }

        else:
            status["content"] = f"Unknown media type returned: {media_type}"
            parsed_data = {
                "status": status,
                "raw_response": raw_response,
            }

        return parsed_data

    def process_failed_response(self, raw_response):
        status = {
            "http_status_code": raw_response.status_code,
            "http_reason": get_response_reason(raw_response),
        }

        try:
            content_data = raw_response.json()
            content_error = content_data.get("error")

            if content_error:
                status["error"] = content_error
                error_code = content_error.get("code")
                error_message = content_error.get("message")

            else:
                error_code = raw_response.status_code
                error_message = raw_response.text

        except (ValueError, TypeError, JSONDecodeError):
            error_code = raw_response.status_code
            error_message = raw_response.text

        parsed_data = {
            "status": status,
            "error_code": error_code,
            "error_message": error_message,
            "raw_response": raw_response,
        }

        return parsed_data

    def parse_raw_response(self, raw_response, *args, **kwargs):
        parsed_data = {}
        is_success = False

        if raw_response is None:
            return is_success, parsed_data

        is_success = raw_response.status_code is requests.codes.ok

        if is_success:
            parsed_data = self.process_successful_response(raw_response)

        else:
            parsed_data = self.process_failed_response(raw_response)

        return is_success, parsed_data


# ---------------------------------------------------------------------------
#   Content data validator
# ---------------------------------------------------------------------------


class ContentValidator:
    def validate_content_data(self, data):
        is_valid = True
        content_data = data.get("content_data")
        status = content_data.get("status")

        if status == "Error":
            is_valid = False
            data["error_code"] = content_data.get("code", -1)
            data["error_message"] = content_data.get("message")

        return is_valid


# ---------------------------------------------------------------------------
#   Data provider
# ---------------------------------------------------------------------------


class DataProvider:
    def __init__(
        self,
        connection=HttpSessionConnection(),
        request=RequestFactory(),
        response=ResponseFactory(),
        parser=Parser(),
        validator=ContentValidator(),
    ):
        self.connection = connection
        self.request = request
        self.response = response
        self.parser = parser
        self.validator = validator

    def get_data(self, *args, **kwargs):
        request = self.request.create(*args, **kwargs)
        raw_response = self.connection.send(request, *args, **kwargs)
        is_success, data = self.parser.parse_raw_response(raw_response)

        if is_success:
            is_success = self.validator.validate_content_data(data)

        if is_success:
            response = self.response.create_success(data, *args, **kwargs)

        else:
            response = self.response.create_fail(data, *args, **kwargs)

        return response

    async def get_data_async(self, *args, **kwargs):
        request = self.request.create(*args, **kwargs)
        raw_response = await self.connection.send_async(request, *args, **kwargs)
        is_success, data = self.parser.parse_raw_response(raw_response)

        if is_success:
            is_success = self.validator.validate_content_data(data)

        if is_success:
            response = self.response.create_success(data, *args, **kwargs)

        else:
            response = self.response.create_fail(data, *args, **kwargs)

        return response


# ---------------------------------------------------------------------------
#   Provider layer
# ---------------------------------------------------------------------------


def emit_event(handler, *args, **kwargs):
    session = args[2]
    if session.has_same_loop():
        try:
            handler(*args, **kwargs)
        except Exception as e:
            session.error(f"{handler} callback raised exception: {e!r}")
            session.debug(traceback.format_exc())
    else:
        session.call_soon_threadsafe(handler, *args, **kwargs)


class ContentProviderLayer:
    def __init__(self, content_type, **kwargs):
        self._kwargs = kwargs
        self._kwargs["__content_type__"] = content_type

        from ._content_provider_factory import make_provider, get_url, get_api_config

        self._content_type = content_type
        self._provider = make_provider(content_type)
        self._url = get_url(content_type)

        api_config = get_api_config(content_type)
        self._auto_retry = api_config.get("auto-retry", False)

    def get_data(self, session=None, on_response=None, **kwargs):
        """
        Returns a response to the data platform

        Parameters
        ----------
        session : Session, optional
            Means default session would be used
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        Response

        Raises
        ------
        AttributeError
            If user didn't set default session.

        """
        session = get_valid_session(session)

        response = self._provider.get_data(
            session, self._url, auto_retry=self._auto_retry, **kwargs, **self._kwargs
        )
        on_response and emit_event(on_response, response, self, session)
        return response

    async def get_data_async(self, session=None, on_response=None, **kwargs):
        """
        Returns a response asynchronously to the data platform

        Parameters
        ----------
        session : Session, optional
            Means default session would be used
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        Response

        Raises
        ------
        AttributeError
            If user didn't set default session.

        """
        session = get_valid_session(session)
        response = await self._provider.get_data_async(
            session, self._url, auto_retry=self._auto_retry, **kwargs, **self._kwargs
        )
        on_response and emit_event(on_response, response, self, session)
        return response

    def __repr__(self):
        repr_str = super().__repr__()
        repr_str = repr_str.replace(">", f" {{name='{self._kwargs.get('universe')}'}}>")
        return repr_str
