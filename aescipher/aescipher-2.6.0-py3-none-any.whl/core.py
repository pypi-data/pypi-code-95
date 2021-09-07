from Crypto import Random
from Crypto.Cipher import AES
from omnitools import sha256d, str_or_bytes, b64e, b64d, try_utf8e, try_utf8d


__ALL__ = ["AESCipher"]


class AESCipher:
    def __init__(self, key: str_or_bytes) -> None:
        self.__cipher = lambda iv: AES.new(sha256d(key), AES.MODE_CBC, iv)

    def encrypt(self, raw: str_or_bytes) -> str:
        raw = try_utf8e(self.__pad(try_utf8e(raw)))
        iv = Random.new().read(AES.block_size)
        return b64e(iv + self.__cipher(iv).encrypt(raw))

    def decrypt(self, enc: str) -> str_or_bytes:
        enc = b64d(enc)
        iv = enc[:AES.block_size]
        return try_utf8d(self.__unpad(self.__cipher(iv).decrypt(enc[AES.block_size:])))

    def destroy(self):
        self.__cipher = None

    @staticmethod
    def __pad(s: str_or_bytes) -> str_or_bytes:
        gap = AES.block_size - len(s) % AES.block_size
        if isinstance(s, bytes):
            char = bytes([gap])
        else:
            char = chr(gap)
        s = s + char * gap
        return s

    @staticmethod
    def __unpad(s: str_or_bytes) -> str_or_bytes:
        s = s[:-ord(s[len(s)-1:])]
        return s


