"""

"""
import hashlib
import configparser
from .exception import HandleError

hash_strategy_func_map = {'hmac-sha1': hashlib.sha1, 'hmac-sha256': hashlib.sha256, 'hmac-sha512': hashlib.sha512}
get_hash_strategy_func = lambda x: hash_strategy_func_map[x]


class Conf:
    def __init__(self, gateway_url: str, access_key: str, secret_key: str, hash_strategy: str,
                 signer_headers: list):
        self.gateway_url = gateway_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.hash_strategy = hash_strategy

        try:
            self.hash_strategy_func = get_hash_strategy_func(hash_strategy)
        except KeyError:
            raise HandleError(f'未知哈希策略，{hash_strategy}')

        self.signer_headers = signer_headers


def new_conf() -> Conf:
    """ 从配置文件实例化配置策略

    """
    import ast
    import os

    config = configparser.ConfigParser()
    if os.environ.get('CMDB_GW_SDK_CONF'):
        config.read(os.environ.get('CMDB_GW_SDK_CONF'))
    else:
        config.read('./conf.ini')

    default_conf = config['DEFAULT']
    gateway_url = default_conf['gateway_url']
    hash_strategy = default_conf['hash_strategy']
    access_key = default_conf['access_key']
    secret_key = default_conf['secret_key']
    signer_headers = ast.literal_eval(default_conf['signer_headers'])

    return Conf(gateway_url=gateway_url, access_key=access_key, secret_key=secret_key,
                hash_strategy=hash_strategy, signer_headers=signer_headers)


