from bitstring import BitArray, ConstBitStream
from .field_codec import FieldCodec
import field_codecs as field_codecs
from typing import List


class FixedLenArrayCodec(FieldCodec):
    def __init__(self, element_type: str, length: int, element_params=None, **kwargs):
        self.length = length
        if element_params:
            self.element_field_codec = field_codecs.field_codec_classes[element_type](**element_params)
        else:
            self.element_field_codec = field_codecs.field_codec_classes[element_type]()

    def encode(self, value: List):
        value = value[0:self.length]
        value_bits = BitArray()
        encoded_value_list = []
        for element in value:
            element_bits, element_value = self.element_field_codec.encode(element)
            value_bits.append(element_bits)
            encoded_value_list.append(element_value)
        return value_bits, encoded_value_list

    def decode(self, bits_to_decode: ConstBitStream):
        decoded_list = []
        for i in range(self.length):
            element = self.element_field_codec.decode(bits_to_decode)
            decoded_list.append(element)
        return decoded_list

    @property
    def min_length_bits(self):
        return self.length * self.element_field_codec.max_length_bits

    @property
    def max_length_bits(self):
        return self.length * self.element_field_codec.max_length_bits