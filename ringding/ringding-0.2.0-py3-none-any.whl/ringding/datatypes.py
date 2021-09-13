
class RdError(Exception):
    """
    Base class for ringding-specific errors.
    """
    pass


class ServerError(RdError):
    """
    An error which occured when executing the user-code.
    """
    pass


class NoAccessError(RdError):
    """
    An error that occurs when class member is called that you don't have access to.
    """
    pass


class NoMemberError(RdError):
    """
    An error that occurs when class member is called that does not exist.
    """
    pass


class HandshakeError(RdError):
    """Error is thrown when a handshake with a client fails."""
