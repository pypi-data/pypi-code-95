import torch
from torch.nn.functional import gelu

from .base_modules import Linear


class TransformerFFN(torch.nn.Module):
    def __init__(self, dim: int, dim_hidden: int):
        super(TransformerFFN, self).__init__()
        self.lin1 = Linear(dim, dim_hidden)
        self.lin2 = Linear(dim_hidden, dim)

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        tensor = self.lin1(tensor)
        tensor = gelu(tensor)
        return self.lin2(tensor)
