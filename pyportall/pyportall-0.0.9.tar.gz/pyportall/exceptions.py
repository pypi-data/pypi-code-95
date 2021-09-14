"""PyPortall custom exceptions."""

class PyPortallException(Exception):
    """Generic API exception."""

    pass


class PreFlightException(PyPortallException):
    """Raised in preflight mode, includes the number of estimated credits that the actual request would consume."""

    def __init__(self, credits, *args) -> None:
        """Constructor.

        Args:
            credits: Number of credits the request will cost.
        """

        self.credits = credits

        super().__init__(*args)


class TimeoutError(PyPortallException):
    """A regular (non-batch) request has timed out."""

    pass


class AuthError(PyPortallException):
    """Authentication has failed, probably because of a wrong API key."""

    pass


class ValidationError(PyPortallException):
    """API is complaining the format of the request is not valid."""

    pass


class BatchError(PyPortallException):
    """A batch request has failed, because of an error or because the batch timeout has expired."""
    pass


class RateLimitError(PyPortallException):
    """The request cannot be fulfilled because either the company credit has run out or the maximum number of allowed requests per second has been exceeded."""

    pass
