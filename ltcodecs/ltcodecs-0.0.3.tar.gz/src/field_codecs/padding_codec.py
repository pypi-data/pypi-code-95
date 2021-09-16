from bitstring import BitArray, ConstBitStream
from .field_codec import FieldCodec


class PaddingCodec(FieldCodec):
    def __init__(self, num_bits, **kwargs):
        self.num_bits = int(num_bits)
        pass

    def encode(self, value=None):
        value_bits = BitArray(uint=0, length=self.num_bits)
        return value_bits, None

    def decode(self, bits_to_decode: ConstBitStream):
        bits_to_decode.read('pad:{}'.format(self.num_bits))
        return None

    def min_length_bits(self):
        return self.num_bits

    def max_length_bits(self):
        return self.num_bits