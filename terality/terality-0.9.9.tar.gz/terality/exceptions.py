class TeralityError(Exception):
    """Base class for errors thrown by the Terality client."""


class TeralityServerError(TeralityError):
    """A server error occured. The operation can be retried."""


class TeralityClientError(TeralityError):
    """A client error occured. Retrying won't help."""
