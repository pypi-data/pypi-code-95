import torch as tr
import numpy as np
from typing import List, Union

class Message:
    def __init__(self, path:List, input:Union[np.ndarray, tr.Tensor], output:Union[np.ndarray, tr.Tensor]):
        self.path = path
        self.input = input
        self.output = output
        assert isinstance(self.path, list), "Wrong type: %s" % type(self.path)
        assert isinstance(self.input, (np.ndarray, tr.Tensor)), "Wrong type: %s" % type(self.input)
        assert isinstance(self.output, (np.ndarray, tr.Tensor)), "Wrong type: %s" % type(self.output)
        for p in self.path:
            from .edge import Edge
            assert isinstance(p, (Edge, str))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        strInput = self.input.shape if not self.input is None else None
        Str = "[Message] Path: %s. Input Shape: %s. Output Shape: %s" % (self.path, strInput, self.output.shape)
        return Str

    # These are so we can use sets in the graph library to add unique nodes only.
    def __eq__(self, other):
        Input = self.input.cpu() if isinstance(self.input, tr.Tensor) else self.input
        Other = other.input.cpu() if isinstance(other.input, tr.Tensor) else other.input
        return np.allclose(Input, Other)

    def __hash__(self):
        return hash(tuple(self.path))