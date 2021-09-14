from pycoinmarketcap.response import ResponseStatus
from typing import Dict


class __ResponseError(Exception, ResponseStatus):
    def __init__(self, status: Dict, message: str = "400 Bad Request") -> None:
        self.message = message
        ResponseStatus.__init__(self, status)

    def __str__(self) -> str:
        return f"{self.message} : {self.error_message}"


class ErrorBadRequest(__ResponseError):
    """
    400 Bad Request
    """

    def __init__(self, status: Dict) -> None:
        super().__init__(status, message="400 Bad Request")


class ErrorUnauthorized(__ResponseError):
    """
    401 Unauthorized
    """

    def __init__(self, status: Dict) -> None:
        super().__init__(status, message="401 Unauthorized")


class ErrorForbidden(__ResponseError):
    """
    403 Forbidden
    """

    def __init__(self, status: Dict) -> None:
        super().__init__(status, message="403 Forbidden")


class ErrorTooManyRequests(__ResponseError):
    """
    429 Too Many Requests
    """

    def __init__(self, status: Dict) -> None:
        super().__init__(status, message="429 Too Many Requests")


class ErrorInternalServerError(__ResponseError):
    """
    500 Internal Server Error
    """

    def __init__(self, status: Dict) -> None:
        super().__init__(status, message="500 Internal Server Error")
