from .broker import *
from easyrsa import *
from aescipher import *
from omnitools import key_pair_format, randb, mac, jd


__ALL__ = ["Agent"]


class Agent(object):
    def __init__(self, app_name: str, key_pair: key_pair_format) -> None:
        self.__aese = lambda v, _={}: self.__check() and (
            _.update({0: randb(256)}) or
            (EasyRSA(public_key=key_pair["public_key"]).encrypt(_[0]), AESCipher(_[0]).encrypt(v))
        )
        self.__aesd = lambda k, v: self.__check() and AESCipher(
            EasyRSA(private_key=key_pair["private_key"]).decrypt(k)
        ).decrypt(v)
        self.__sign = lambda m: self.__check() and EasyRSA(private_key=key_pair["private_key"]).sign(m)
        self.__verify = lambda m, s: self.__check() and EasyRSA(public_key=key_pair["public_key"]).verify(m, s)
        self.__setk = lambda k, v: self.__check() and mac(sha3_512hd(k), v)
        self.__setn = lambda v: self.__check() and self.__setk(key_pair["public_key"], v)
        self.__broker = lambda id: self.__check() and Broker(app_name=self.__setn(app_name), username=self.__setn(id))

    @staticmethod
    def __check() -> bool:
        import inspect
        if not inspect.stack()[2][1].replace("\\", ".").replace("/", ".").endswith("-packages.credsafe.agent.py"):
            raise Exception("call outside Agent() is prohibited")
        return True

    def __encrypt(self, v: Any) -> str:
        self.__check()
        sk, v = self.__aese(jd(v))
        sk = b64e(sk)
        hash = b64e(self.__sign(v))
        return "{} {} {}".format(hash, sk, v)

    def set(self, id: str, pw: str, k: str, v: Any) -> Any:
        self.__broker(id).set(self.__setk(pw, k), self.__encrypt(v))
        return self

    def __decrypt(self, v: str) -> Any:
        self.__check()
        hash, sk, v = v.split(" ")
        if self.__verify(v, b64d(hash)):
            return jl(self.__aesd(b64d(sk), v))
        raise Exception("credentials are tampered due to different hmac")

    def get(self, id: str, pw: str, k: str) -> Any:
        return self.__decrypt(self.__broker(id).get(self.__setk(pw, k)))

    def rm(self, id: str, pw: str, k: str) -> bool:
        return self.__broker(id).rm(self.__setk(pw, k))

    def destroy(self, id: str) -> bool:
        return self.__broker(id).destroy()




