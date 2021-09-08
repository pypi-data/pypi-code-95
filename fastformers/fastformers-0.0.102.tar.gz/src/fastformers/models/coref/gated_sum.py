import torch


class GatedSum(torch.nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self._gate = torch.nn.Linear(input_dim * 2, 1)

    def forward(self, input_a: torch.Tensor, input_b: torch.Tensor) -> torch.Tensor:
        gate_value = torch.sigmoid(self._gate(torch.cat([input_a, input_b], -1)))
        return gate_value * input_a + (1 - gate_value) * input_b
