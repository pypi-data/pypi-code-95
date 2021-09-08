class Error(Exception):
    """pass"""


class ServiceDown(Error):
    """pass"""


class InvalidInput(Error):
    """pass"""


class InvalidRequesterInput(Error):
    """pass"""


class ServiceUnavailable(Error):
    """pass"""


class MSUnavailable(Error):
    """pass"""


class Timeout(Error):
    """pass"""


class VATBlocked(Error):
    """pass"""


class IPBlocked(Error):
    """pass"""


class GlobalMaxConcurrentReq(Error):
    """pass"""


class GlobalMaxConcurrentReqTime(Error):
    """pass"""


class MSMaxConcurrentReq(Error):
    """pass"""


class MsGlobalMaxConcurrentReqTime(Error):
    """pass"""


class OtherError(Error):
    """pass"""


EXCEPTION_MAP = {
    "INVALID_INPUT": InvalidInput,
    "INVALID_REQUESTER_INFO": InvalidRequesterInput,
    "SERVICE_UNAVAILABLE": ServiceUnavailable,
    "MS_UNAVAILABLE": MSUnavailable,
    "TIMEOUT": Timeout,
    "VAT_BLOCKED": VATBlocked,
    "IP_BLOCKED": IPBlocked,
    "GLOBAL_MAX_CONCURRENT_REQ": GlobalMaxConcurrentReq,
    "GLOBAL_MAX_CONCURRENT_REQ_TIME": GlobalMaxConcurrentReqTime,
    "MS_MAX_CONCURRENT_REQ": MSMaxConcurrentReq,
    "MS_MAX_CONCURRENT_REQ_TIME": MsGlobalMaxConcurrentReqTime,
}
