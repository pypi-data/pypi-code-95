import json
import socket
import pickle
import threading
import traceback
from .utils import *
from omnitools import encryptedsocket_function, p, utf8d, dt2yyyymmddhhmmss


__ALL__ = ["SS"]


class SS:
    def __init__(self, functions: encryptedsocket_function = None,
                 host: str = "127.199.71.10", port: int = 39291,
                 silent: bool = False) -> None:
        self.terminate = False
        self.silent = silent
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, int(port)))
        self.s.listen(5)
        self.__key = {}
        self.functions = functions or {}

    def handler(self, conn: socket.socket, addr: tuple) -> None:
        uid = "{}:{}".format(*addr)
        if not self.silent:
            p("{}\tconnected\t{}".format(dt2yyyymmddhhmmss(), uid))
        try:
            while True:
                request = recv_all(conn)
                if not request:
                    break
                try:
                    request = json.loads(utf8d(request))
                except:
                    request = pickle.loads(request)
                try:
                    if request["command"] in self.functions:
                        response = self.functions[request["command"]](*request["data"][0], **request["data"][1])
                    else:
                        raise Exception("request command '{}' is not in socket functions".format(request["command"]))
                except:
                    response = traceback.format_exc()
                try:
                    response = json.dumps(response).encode()
                except TypeError:
                    response = pickle.dumps(response)
                conn.sendall(struct.pack('>I', len(response))+response)
        except Exception as e:
            p(e)
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

