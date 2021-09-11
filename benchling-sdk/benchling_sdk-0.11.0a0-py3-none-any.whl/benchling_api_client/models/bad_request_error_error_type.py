from enum import Enum


class BadRequestErrorErrorType(str, Enum):
    INVALID_REQUEST_ERROR = "invalid_request_error"

    def __str__(self) -> str:
        return str(self.value)
