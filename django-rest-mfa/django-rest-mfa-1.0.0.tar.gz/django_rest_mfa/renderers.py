from rest_framework import renderers
from rest_framework.utils.encoders import JSONEncoder
from fido2.utils import websafe_encode, websafe_decode
from fido2 import cbor


class Base64JSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return websafe_encode(obj)
        return super().default(obj)


class CBORRenderer(renderers.BaseRenderer):
    """
    Concise Binary Object Representation Renderer
    """

    format = 'cbor'
    media_type = "application/octet-stream"

    def render(self, data, media_type=None, renderer_context=None):
        return cbor.encode(data)


class Base64JSONRenderer(renderers.JSONRenderer):
    encoder_class = Base64JSONEncoder
