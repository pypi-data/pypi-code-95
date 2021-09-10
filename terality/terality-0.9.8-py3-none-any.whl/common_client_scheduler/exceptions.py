from abc import ABC
from dataclasses import dataclass

from terality_serde import SerdeMixin


@dataclass
class TeralityError(Exception, SerdeMixin, ABC):
    """Deprecated. Base class for all Terality errors (propagated to the client)'.

    Deprecated: we're moving away from serializing and deserializing exceptions.
    Use ServerErrorResponse and ClientErrorResponse instead.
    """

    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TeralityAuthError(TeralityError):
    pass


class TeralityInternalError(TeralityError):
    pass


class TeralityInvalidRequest(TeralityError):
    pass


class TeralityQuotaExceeded(TeralityError):
    pass


class TeralityAccountCreationError(TeralityError):
    pass
