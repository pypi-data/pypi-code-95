from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import ceil, log2


class CclLatLonCodec(FieldCodec):
    def __init__(self, **kwargs):
        pass

    def encode(self, value: float):
        encoded_value = int(value * ((2 ** 23 - 1) / 180.0))
        encoded_bits = Bits(intle=encoded_value, length=24)

        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream):
        scale = bits_to_decode.read('intle:24')
        value = scale * (180.0 / (2**23 - 1))
        return value

    @property
    def max_length_bits(self):
        return 24

    @property
    def min_length_bits(self):
        return 24