from easyrsa import *
from omnitools import randb


kp = EasyRSA(bits=1024).gen_key_pair()
print(kp)
print(EasyRSA(public_key=kp["public_key"]).max_msg_size())
print(EasyRSA(private_key=kp["private_key"]).max_msg_size())

from base64 import b64encode
symmetric_key = "abc"*1000 or b"abc" or b64encode(b"abc")
encrypted_key = EasyRSA(public_key=kp["public_key"]).encrypt(symmetric_key)
print(encrypted_key)
print(symmetric_key == EasyRSA(private_key=kp["private_key"]).decrypt(encrypted_key))

msg = randb(1024)
s = EasyRSA(private_key=kp["private_key"]).sign(msg)
print(msg, s)
print(EasyRSA(public_key=kp["public_key"]).verify(msg, s))
