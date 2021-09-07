import socket
import pickle
import struct
from .utils import *
from omnitools import jd_and_utf8e, utf8d, args, randb
from easyrsa import *


__ALL__ = ["SC"]


class SC(object):
    def __init__(self, host: str = "127.199.71.10", port: int = 39291) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, int(port)))
        self.key = None
        hash, public_key = self.request("get_pkey")
        public_key = b64d(public_key)
        rsa = EasyRSA(public_key=public_key)
        if rsa.verify(public_key, b64d(hash)):
            key = randb(256)
            self.request(command="set_key", data=args(b64e(rsa.encrypt(key))))
            self.key = key
        else:
            raise Exception("current connection is under MITM attack")

    def request(self, command: str, data: Tuple[Tuple, Dict] = args()) -> Any:
        request = dict(command=command, data=data)
        try:
            request = jd_and_utf8e(request)
        except:
            request = pickle.dumps(request)
        if self.key:
            request = encrypt(self.key, request)
        self.s.sendall(struct.pack('>I', len(request))+request)
        response = utf8d(recv_all(self.s))
        if self.key:
            return decrypt(self.key, response)
        else:
            return jl(response)


