from hashlib import sha3_512, sha3_256, sha1, md5, sha256, sha384, sha512
from zlib import crc32
import hmac
from . import str_or_bytes, try_utf8e


__ALL__ = ["sha256d", "sha3_512hd", "mac", "crc32hd", "md5hd", "sha1hd", "sha256hd", "sha384hd", "sha512hd"]


def sha256d(content: str_or_bytes) -> bytes:
    return sha3_256(try_utf8e(content)).digest()


def sha3_512hd(content: str_or_bytes) -> str:
    return sha3_512(try_utf8e(content)).hexdigest()


def mac(key: str_or_bytes, content: str_or_bytes, method=sha3_512) -> str:
    return hmac.new(try_utf8e(key), try_utf8e(content), method).hexdigest()


def crc32hd(_input):
    hd = 0
    if hasattr(_input, "seek") and hasattr(_input, "read"):
        _input.seek(0)
        while True:
            data = _input.read(1024*8)
            if not data:
                break
            hd = crc32(data, hd)
        _input.seek(0)
    elif isinstance(_input, (str, bytes)):
        hd = crc32(try_utf8e(_input), hd)
    else:
        raise Exception(f"input type {type(_input)} not implemented")
    return format(hd, "x").zfill(8)


def _hd_update(_input, hd) -> str:
    if isinstance(_input, _io.BufferedReader):
        _input.seek(0)
        while True:
            data = _input.read(1024*8)
            if not data:
                break
            hd.update(data)
        _input.seek(0)
    elif isinstance(_input, (str, bytes)):
        hd.update(try_utf8e(_input))
    else:
        raise Exception(f"input type {type(_input)} not implemented")
    return hd.hexdigest()


def md5hd(_input) -> str:
    return _hd_update(_input, md5())


def sha1hd(_input) -> str:
    return _hd_update(_input, sha1())


def sha256hd(_input) -> str:
    return _hd_update(_input, sha256())


def sha384hd(_input) -> str:
    return _hd_update(_input, sha384())


def sha512hd(_input) -> str:
    return _hd_update(_input, sha512())

