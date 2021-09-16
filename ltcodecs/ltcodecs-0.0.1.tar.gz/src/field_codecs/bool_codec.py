from bitstring import BitArray, ConstBitStream
from .field_codec import FieldCodec


class BoolCodec(FieldCodec):
    def __init__(self, **kwargs):
        pass

    def encode(self, value: bool):
        value = bool(value)
        value_bits = BitArray(bool=value)
        return value_bits, value

    def decode(self, bits_to_decode: ConstBitStream):
        value = bits_to_decode.read('bool')
        return value

    def min_length_bits(self):
        return 1

    def max_length_bits(self):
        return 1