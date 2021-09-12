import typing

__all__: typing.List[str] = [
    "XivError",
    "FailedRequest",
]


class XivError(Exception):
    """Base exepction, that all xivapyi errors derive from."""

    ...


class FailedRequest(XivError):
    """Raised when a non 200 response is received from XIVAPI."""

    ...
