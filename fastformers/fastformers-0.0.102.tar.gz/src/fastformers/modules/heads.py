import torch

from .base_modules import Linear


class TanhHead(torch.nn.Module):
    """Head for sentence-level classification tasks."""

    def __init__(self, input_dim: int, inner_dim: int, num_classes: int):
        super().__init__()
        self.dense = Linear(input_dim, inner_dim)
        self.out_proj = Linear(inner_dim, num_classes)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = torch.tanh(hidden_states)
        return self.out_proj(hidden_states)
