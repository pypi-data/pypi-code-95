from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import ceil, log2


class IeeeFloatCodec(FieldCodec):
    def __init__(self, num_bits=32, **kwargs):
        if num_bits not in (32, 64):
            raise ValueError("Only 32 or 64 bit widths are supported for IEEE floating point codecs")
        self.num_bits = num_bits

    def encode(self, value: float):
        value = float(value)
        encoded_bits = Bits(float=value, length=self.num_bits)
        encoded_value = encoded_bits.float
        ## print("encode varint {} bits as {}".format(num_bits, encoded_bits))
        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream):
        value = bits_to_decode.read('floatbe:{}'.format(self.num_bits))
        return value

    @property
    def max_length_bits(self):
        return self.num_bits

    @property
    def min_length_bits(self):
        return self.num_bits


class IeeeFloat32Codec(IeeeFloatCodec):
    def __init__(self, **kwargs):
        super(IeeeFloat32Codec, self).__init__(num_bits=32)


class IeeeFloat64Codec(IeeeFloatCodec):
    def __init__(self, **kwargs):
        super(IeeeFloat64Codec, self).__init__(num_bits=64)