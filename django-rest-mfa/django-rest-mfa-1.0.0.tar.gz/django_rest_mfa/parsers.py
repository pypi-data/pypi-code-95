from rest_framework import parsers
from .renderers import Base64JSONRenderer
from fido2 import cbor


class CBORParser(parsers.BaseParser):
    """
    Concise Binary Object Representation Parser
    """

    media_type = "application/cbor"

    def parse(self, stream, media_type=None, parser_context=None):
        content = stream.read()
        return cbor.decode(content)


class Base64JSONParser(parsers.JSONParser):
    renderer_class = Base64JSONRenderer
