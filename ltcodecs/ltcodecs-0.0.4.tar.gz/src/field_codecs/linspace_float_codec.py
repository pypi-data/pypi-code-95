from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import ceil, log2


class LinspaceFloatCodec(FieldCodec):
    def __init__(self, min_value: float, max_value: float,
                 resolution: float = None, num_values: int = None, num_bits: int = None, **kwargs):
        self.max_value = float(max_value)
        self.min_value = float(min_value)
        self.value_range = max_value - min_value
        if num_values or num_bits:
            if resolution:
                raise ValueError("LinspaceFloatCodec supports setting only one of num_values, num_bits, or resolution.")
            if num_bits:
                if num_values:
                    raise ValueError("LinspaceFloatCodec supports setting either num_values or num_bits, not both.")
                num_values = 2 ** num_bits
            resolution = self.value_range / num_values

        self.resolution = float(resolution)

        self.num_values = self.value_range // self.resolution
        # if the max value isn't an integer multiple of the resolution from the min value, it won't be encoded.
        self.num_bits = ceil(log2(self.num_values))

    def encode(self, value: float):
        value = float(value)
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        offset = value - self.min_value
        discretized_offset = int(offset // self.resolution)
        encoded_value = self.min_value + (discretized_offset * self.resolution)
        encoded_bits = Bits(uint=discretized_offset, length=self.num_bits)
        ## print("encode varint {} bits as {}".format(num_bits, encoded_bits))
        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream):
        discretized_offset = bits_to_decode.read('uint:{}'.format(self.num_bits))
        value = self.min_value + (discretized_offset * self.resolution)
        return value

    @property
    def max_length_bits(self):
        return self.num_bits

    @property
    def min_length_bits(self):
        return self.num_bits