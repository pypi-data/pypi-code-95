from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import ceil, log2


class VarintCodec(FieldCodec):
    def __init__(self, min_value: int, max_value: int, resolution: int = 1, little_endian: bool = False, **kwargs):
        self.max_value = int(max_value)
        self.min_value = int(min_value)
        self.resolution = int(resolution)

        self.value_range = max_value - min_value
        num_values = (self.value_range // self.resolution) + 1
        self.num_bits = ceil(log2(num_values))
        self.little_endian = little_endian

    def encode(self, value: int):
        value = int(value)
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        offset = value - self.min_value
        discretized_offset = offset // self.resolution
        encoded_value = self.min_value + (discretized_offset * self.resolution)
        if self.little_endian:
            encoded_bits = Bits(uintle=discretized_offset, length=self.num_bits)
        else:
            encoded_bits = Bits(uint=discretized_offset, length=self.num_bits)
        ## print("encode varint {} bits as {}".format(num_bits, encoded_bits))
        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream):
        if self.little_endian:
            discretized_offset = bits_to_decode.read('uintle:{}'.format(self.num_bits))
        else:
            discretized_offset = bits_to_decode.read('uint:{}'.format(self.num_bits))

        value = self.min_value + (discretized_offset * self.resolution)
        return value

    @property
    def max_length_bits(self):
        return self.num_bits

    @property
    def min_length_bits(self):
        return self.num_bits

    def __repr__(self):
        return "VarintCodec {:x}: min_value={}, max_value={}, resolution={}".format(id(self),
                                                                                    self.min_value,
                                                                                    self.max_value,
                                                                                    self.resolution)