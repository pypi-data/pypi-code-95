from typing import Union, List

import torch
from torch.nn.functional import relu


class FeedForward(torch.nn.Module):
    def __init__(self, input_dim: int, num_layers: int, dims: Union[int, List[int]]):

        super().__init__()
        if isinstance(dims, int):
            dims = [dims] * num_layers
        if len(dims) != num_layers:
            raise ValueError('len(hidden_dims) (%d) != num_layers (%d)' % (len(dims), num_layers))
        input_dims = [input_dim] + dims[:-1]
        self._linear_layers = torch.nn.ModuleList(
            torch.nn.Linear(layer_input_dim, layer_output_dim)
            for layer_input_dim, layer_output_dim in zip(input_dims, dims)
        )
        self._output_dim = dims[-1]
        self.input_dim = input_dim

    def get_output_dim(self):
        return self._output_dim

    def get_input_dim(self):
        return self.input_dim

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        for layer in self._linear_layers:
            tensor = relu(layer(tensor))
        return tensor
