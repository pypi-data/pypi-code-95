import socket
import pickle
import json
from .utils import *
from omnitools import args, utf8d


__ALL__ = ["SC"]


class SC:
    def __init__(self, host: str = "127.199.71.10", port: int = 39291) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, int(port)))

    def request(self, command: str, data: Tuple[Tuple, Dict] = args()):
        request = dict(command=command, data=data)
        try:
            request = json.dumps(request).encode()
        except:
            request = pickle.dumps(request)
        import struct
        self.s.send(struct.pack('>I', len(request))+request)
        response = recv_all(self.s)
        try:
            return json.loads(utf8d(response))
        except UnicodeDecodeError:
            return pickle.loads(response)

