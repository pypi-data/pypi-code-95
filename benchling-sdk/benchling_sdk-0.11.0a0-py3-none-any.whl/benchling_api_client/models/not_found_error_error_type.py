from enum import Enum


class NotFoundErrorErrorType(str, Enum):
    INVALID_REQUEST_ERROR = "invalid_request_error"

    def __str__(self) -> str:
        return str(self.value)
