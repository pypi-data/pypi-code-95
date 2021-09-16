from abc import ABC, abstractmethod

class FieldCodec(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def encode(self):
        pass

    @abstractmethod
    def decode(self):
        pass

    @property
    @abstractmethod
    def max_length_bits(self):
        pass

    @property
    @abstractmethod
    def min_length_bits(self):
        pass