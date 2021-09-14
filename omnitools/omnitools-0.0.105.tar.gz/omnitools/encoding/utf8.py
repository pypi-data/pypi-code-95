from ..xtypes import *

__ALL__ = ["utf8e", "utf8d", "try_utf8d", "try_utf8e"]


def utf8e(s: str) -> bytes:
    return s.encode("utf-8")


def utf8d(b: bytes) -> str:
    return b.decode("utf-8")


def try_utf8d(b: str_or_bytes) -> str:
    try:
        return utf8d(b)
    except:
        return b


def try_utf8e(s: str_or_bytes) -> bytes:
    try:
        return utf8e(s)
    except:
        return s


