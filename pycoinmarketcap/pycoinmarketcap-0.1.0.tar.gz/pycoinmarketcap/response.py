from typing import Dict, Generic, TypeVar

T = TypeVar("T")


class Response(Generic[T]):
    """
    Response object for all requests / function calls.

    Attributes
    ----------
    data: T
        Data content of response
    status: ResponseStatus
        Standardized status response for API calls.
    """

    def __init__(self, response: Dict) -> None:
        """Parameters

        Args:
            response (Dict): The response json.
        """
        self.data: T = response["data"]
        self.status = ResponseStatus(response["status"])


class ResponseStatus:
    """
    Standardized status object for API calls.

    Attributes
    ----------
    timestamp: str
        Current ISO 8601 timestamp on the server.
    error_code: int
        An internal error code for the current error. If a unique platform error code
        is bot available the HTTP status code is returned. (default: 400)
    error_message: str
        An error message to go along with the error code.
    elapsed: int
        Number of milliseconds taken to generate this response.
    credit_count: int
        Number of API call credits required for this call. Always 0 for errors.
    """

    def __init__(self, status: Dict) -> None:
        """Parameters

        Args:
            status (Dict): The status response object.
        """

        self.timestamp = status.get("timestamp", "")
        self.error_code = status.get("error_code", 400)
        self.error_message = status.get("error_message", "")
        self.elapsed = status.get("elapsed", 0)
        self.credit_count = status.get("credit_count", 0)
