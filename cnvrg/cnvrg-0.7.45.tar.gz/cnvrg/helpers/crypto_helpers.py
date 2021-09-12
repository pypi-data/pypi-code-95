from Crypto.Cipher import AES
from base64 import b64decode
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def decrypt(key: str, iv: str, secret: str):
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, b64decode(iv.encode("utf8")))
    secret = b64decode(secret.encode("utf-8"))
    return unpad(cipher.decrypt(secret).decode('utf8'))