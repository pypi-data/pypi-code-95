import hashlib
import hmac
import base64
from .exception import HandleError
from .conf_parser import Conf


def hmac_signer(message: bytes, conf: Conf) -> bytes:
    """hmac签名并用b64编码

    ARGS:
        message(bytearray)
        conf(Conf)

    RETURNS:
        byte
    """

    return base64.b64encode(hmac.new(bytes(conf.secret_key, 'utf-8'), message, conf.hash_strategy_func).digest())
