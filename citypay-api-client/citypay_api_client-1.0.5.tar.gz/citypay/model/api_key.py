# coding: utf-8
from datetime import datetime
import hmac
import hashlib
import base64
import os


def api_key_generate(client_id, licence_key):
    return api_key_generate_for(client_id, licence_key, os.urandom(16), datetime.utcnow())


def api_key_generate_for(client_id: str, licence_key: str, nonce: bytes, dt: datetime) -> str:
    """
    @param client_id: the client id used for processing
    @param licence_key: a licence key provided
    @param nonce: a random 16 byte value
    @param dt: current datetime
    @return: a base64 encoded api key
    """
    ds = dt.strftime("%Y%m%d%H%M")
    message = bytearray()
    message += bytes(client_id, 'utf-8')
    message += nonce
    message += bytes.fromhex(ds)
    digest = hmac.new(bytes(licence_key, 'utf-8'),
                      msg=message,
                      digestmod=hashlib.sha256).digest()
    dest = bytearray()
    dest += bytes(client_id, 'utf-8')
    dest += b'\x3A'
    dest += bytes(nonce.hex().upper(), 'utf-8')
    dest += b'\x3A'
    dest += digest
    return base64.b64encode(dest).decode('utf-8')
