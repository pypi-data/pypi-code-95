import torch


class TimeDistributed(torch.nn.Module):
    def __init__(self, module):
        super().__init__()
        self._module = module

    def get_input_dim(self) -> int:
        return self._module.get_input_dim()

    def get_output_dim(self) -> int:
        return self._module.get_output_dim()

    def forward(self, inputs):
        outputs = self._module(inputs.flatten(0, 1))
        return outputs.view(inputs.shape[:2] + outputs.shape[1:])
