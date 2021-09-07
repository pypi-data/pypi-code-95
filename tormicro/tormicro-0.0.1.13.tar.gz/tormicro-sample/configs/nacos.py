import base64
import hashlib
import hmac
import time

import requests
import yaml

from tormicro.config import ConfigDict

_SERVER_ROUTE_PORT = 8080
_SERVER_ROUTE_URI = '/diamond-server/diamond'
_CONFIG_QUERY_PORT = 8848
_CONFIG_QUERY_URI = '/nacos/v1/cs/configs'


def _hmac_sha1_sign(content: str, sk: str):
    sign = hmac.new(bytes(sk, encoding='utf-8'), bytes(content, encoding='utf-8'), hashlib.sha1).digest()
    base64sign = base64.b64encode(sign)
    return base64sign.decode('utf-8')


def load_config_nacos(bootstrap: ConfigDict, env: str, workdir: str) -> ConfigDict:
    nacos = bootstrap.config.nacos
    c = ConfigDict({**nacos.to_dict(), **(nacos[env].to_dict() if env in nacos.to_dict() else dict())})

    with requests.get(f'http://{c.endpoint}:{_SERVER_ROUTE_PORT}{_SERVER_ROUTE_URI}') as resp:
        if resp.ok:
            server_ip = resp.text.strip()

    if not server_ip:
        raise RuntimeError("load nacos config failed")

    timestamp = int(time.time() * 1000)
    sign_str = c.namespace + '+' + c.group + '+' + str(timestamp)

    params = dict(
        dataId=c.dataId,
        group=c.group,
        tenant=c.namespace
    )

    headers = {
        'Spas-AccessKey': c.accessKey,
        'Timestamp': str(timestamp),
        'Spas-Signature': _hmac_sha1_sign(sign_str, c.secretKey)
    }

    with requests.get(f'http://{server_ip}:{_CONFIG_QUERY_PORT}{_CONFIG_QUERY_URI}', params=params, headers=headers) as resp:
        if resp.ok:
            return ConfigDict(yaml.load(resp.text, Loader=yaml.SafeLoader))

    return ConfigDict()

