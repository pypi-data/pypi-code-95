import base64

from codefast.utils import deprecated

from .toolkits.endecode import decode_with_keyfile, encode_with_keyfile
from .pipe import author

@deprecated('decode() is deprecated, use pipe.author.get() instead.')
def decode(keyword: str) -> str:
    from .pipe import author
    return author.get(keyword)


def fast_text_encode(text: str) -> str:
    ''' Encode text with passphrase in js[auth_file]'''
    return encode_with_keyfile(author.get('auth'), text)


def fast_text_decode(text: str):
    return decode_with_keyfile(author.get('auth'), text)
