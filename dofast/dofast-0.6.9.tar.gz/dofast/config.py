import base64

import codefast as cf

from .core import InitConfig
from .toolkits.endecode import decode_with_keyfile, encode_with_keyfile

FILEDN_CODE = 'lCdtpv3siVybVynPcgXgnPm'
SERVER_HOST = base64.urlsafe_b64decode(b'YS5kZG90LmNj').decode()
ACCOUNTS = InitConfig.accounts
AUTH_FILE_NAME = base64.urlsafe_b64decode(b'YXV0aF9maWxl').decode()
SALT = ACCOUNTS.get(AUTH_FILE_NAME, '')


def decode(keyword: str) -> str:
    _pass = decode_with_keyfile(SALT, ACCOUNTS[keyword.lower()])
    return _pass


def fast_text_encode(text: str) -> str:
    ''' Encode text with passphrase in js[auth_file]'''
    return encode_with_keyfile(SALT, text)


def fast_text_decode(text: str):
    return decode_with_keyfile(SALT, text)
