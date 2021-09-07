import struct
import socket
import pickle
import threading
from .utils import *
from omnitools import encryptedsocket_function, p, utf8d, key_pair_format, dt2yyyymmddhhmmss
from debugging import *
from easyrsa import *


__ALL__ = ["SS"]


class SS(object):
    def __init__(self, key_pair: key_pair_format, functions: encryptedsocket_function = None,
                 host: str = "127.199.71.10", port: int = 39291,
                 silent: bool = False) -> None:
        self.terminate = False
        self.silent = silent
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, int(port)))
        self.s.listen(5)
        self.__key = {}
        self.functions = functions or {}
        self.rsae = lambda v: EasyRSA(private_key=key_pair["private_key"]).encrypt(v)
        self.sign = lambda v: EasyRSA(private_key=key_pair["private_key"]).sign(v)
        self.rsad = lambda v: EasyRSA(private_key=key_pair["private_key"]).decrypt(v)
        self.pkey = lambda: key_pair["public_key"]

    def handler(self, conn: socket.socket, addr: tuple) -> None:
        uid = "{}:{}".format(*addr)
        if not self.silent:
            p("{}\tconnected\t{}".format(dt2yyyymmddhhmmss(), uid))
        try:
            while True:
                request = utf8d(recv_all(conn))
                if not request:
                    self.__key.pop(uid)
                    break
                if uid in self.__key:
                    request = decrypt(self.__key[uid], request)
                else:
                    request = jl(request)
                try:
                    if request["command"] == "get_pkey" and uid not in self.__key:
                        v = self.pkey()
                        response = (
                            b64e(self.sign(v)),
                            b64e(v)
                        )
                    elif request["command"] in self.functions:
                        response = self.functions[request["command"]](*request["data"][0], **request["data"][1])
                    else:
                        raise Exception("request command '{}' is not in socket functions".format(request["command"]))
                except:
                    response = debug_info()
                try:
                    from omnitools import jd_and_utf8e
                    response = jd_and_utf8e(response)
                except TypeError:
                    response = pickle.dumps(response)
                if uid in self.__key:
                    response = encrypt(self.__key[uid], response)
                conn.sendall(struct.pack('>I', len(response))+response)
                if request["command"] == "set_key" and uid not in self.__key:
                    try:
                        bkey = self.rsad(b64d(request["data"][0][0]))
                    except:
                        raise Exception("current connection is under MITM attack")
                    self.__key[uid] = bkey
        except:
            p(debug_info()[0])
        finally:
            conn.close()
            if not self.silent:
                p("{}\tdisconnected\t{}".format(dt2yyyymmddhhmmss(), uid))

    def start(self) -> None:
        try:
            while not self.terminate:
                conn, addr = self.s.accept()
                threading.Thread(target=self.handler, args=(conn, addr)).start()
        except Exception as e:
            if not self.terminate:
                raise e

    def stop(self) -> bool:
        self.terminate = True
        self.s.close()
        return True


