from core_commons.exceptions import BaseError

# NSXT_ERROR_CODES
NSXT_ERROR = "NSXT000"
NSXT_API_ERROR = "NSXT100"
NSXT_SSH_ERROR = "NSXT200"
NSXT_CLI_ERROR = "NSXT300"


class NSXTError(BaseError):
    """General NSXT error."""

    def __init__(self, message, caused_by=None):
        BaseError.__init__(self, message, NSXT_ERROR, caused_by)


class APIError(NSXTError):
    """Error raised when a API interaction returns an error."""

    def __init__(self, message, status_code=None, caused_by=None):
        BaseError.__init__(self, message, NSXT_API_ERROR, caused_by)
        self.status_code = status_code


class SSHError(NSXTError):
    """ raised when a SSH interaction returns an error."""

    def __init__(self, message, caused_by=None):
        BaseError.__init__(self, message, NSXT_SSH_ERROR, caused_by)


class CLIError(SSHError):
    """Error raised when a CLI interaction returns an error."""

    def __init__(self, message, caused_by=None):
        BaseError.__init__(self, message, NSXT_CLI_ERROR, caused_by)
