from bitstring import BitArray, ConstBitStream
from .field_codec import FieldCodec
from .varint_codec import VarintCodec


class BytesCodec(FieldCodec):
    def __init__(self, max_length: int, **kwargs):
        self.max_length = max_length
        self.length_codec = VarintCodec(min_value=0, max_value=self.max_length)

    def encode(self, value: bytes):
        value = value[0:self.max_length]
        length_bits, _ = self.length_codec.encode(len(value))
        value_bits = BitArray(bytes=value)
        value_bits.prepend(length_bits)
        return value_bits, value

    def decode(self, bits_to_decode: ConstBitStream):
        num_bytes = self.length_codec.decode(bits_to_decode)
        value = bits_to_decode.read('bytes:' + str(num_bytes))
        return value

    def min_length_bits(self):
        return self.length_codec.max_length_bits

    def max_length_bits(self):
        return self.length_codec.max_length_bits + (8 * self.max_length)