import keyring
from omnitools import sha3_512hd, b64d_and_utf8d, jl, jd_and_b64e
from typing import *


__ALL__ = ["Broker"]


class Broker(object):
    def __init__(self, app_name: str, username: str) -> None:
        self.__split_length = 10 ** 3
        self.__krs = lambda i, v: keyring.set_password(sha3_512hd("{}[{}]".format(app_name, i)), username, v)
        self.__krg = lambda i: keyring.get_password(sha3_512hd("{}[{}]".format(app_name, i)), username)
        self.__krd = lambda i: keyring.delete_password(sha3_512hd("{}[{}]".format(app_name, i)), username)
        if len(self.__get()) == 0:
            self.set("", "")

    @staticmethod
    def __check() -> bool:
        import inspect
        if not inspect.stack()[2][1].replace("\\", ".").replace("/", ".").endswith("site-packages.credsafe.broker.py"):
            raise Exception("call outside Broker() is prohibited")
        return True

    def __get(self) -> Dict[str, str]:
        self.__check()
        v = ""
        i = 0
        while True:
            _ = self.__krg(i)
            if _ is None:
                break
            else:
                v += _
                i += 1
        if v == "":
            return {}
        return jl(b64d_and_utf8d(v))

    def get(self, k: str) -> str:
        return self.__get()[k]

    def __set(self, v: Dict[str, str]) -> bool:
        self.__check()
        v = jd_and_b64e(v)
        i = 0
        while v:
            self.__krs(i, v[:self.__split_length])
            v = v[self.__split_length:]
            i += 1
        return self.__delete(i)

    def set(self, k: str, v: str) -> bool:
        _ = self.__get()
        _[k] = v
        return self.__set(_)

    def rm(self, k: str) -> bool:
        _ = self.__get()
        _.pop(k)
        return self.__set(_)

    def __delete(self, i: int = 0) -> bool:
        self.__check()
        while True:
            _ = self.__krg(i)
            if _ is None:
                return True
            else:
                self.__krd(i)
                i += 1

    def destroy(self) -> bool:
        self.__delete()
        self.__krs = None
        self.__krg = None
        self.__krd = None
        return True



