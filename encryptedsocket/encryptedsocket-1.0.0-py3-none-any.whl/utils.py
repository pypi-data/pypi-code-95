from aescipher import *
import pickle
from omnitools import mac, jl
from typing import *
import struct
import socket


__ALL__ = ["encrypt", "decrypt", "recv_all"]


def recv_all(conn: socket.socket) -> bytes:
    length = conn.recv(4)
    if length == b"":
        return b""
    length = struct.unpack('>I', length)[0]
    content = b""
    while len(content) < length:
        content += conn.recv(length-len(content))
        if not content:
            break
    return content


def encrypt(key: str_or_bytes, plaintext: str_or_bytes) -> bytes:
    ciphertext = AESCipher(key).encrypt(plaintext)
    hash = mac(key, ciphertext)
    return "{} {}".format(hash, ciphertext).encode("utf-8")


def decrypt(key: str_or_bytes, ciphertext: str) -> Any:
    hash, ciphertext = ciphertext.split(" ")
    if hash == mac(key, ciphertext):
        ciphertext = AESCipher(key).decrypt(ciphertext)
        try:
            return jl(ciphertext)
        except:
            return pickle.loads(ciphertext)
    else:
        raise Exception("current connection might be spoofed due to different hmac.")




