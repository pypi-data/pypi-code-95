import torch.nn.functional as F
import torch.nn as nn
from torch import Tensor


class Identity(nn.Module):
    def __init__(self) -> None:
        super(Identity, self).__init__()

    def forward(self, input: Tensor) -> Tensor:
        return input


class BNReLU(nn.Module):
    r"""
    A batch-normalization layer followed by relu.

    Args:
        in_channels (int): Number of channels in the input image.
        affine: A boolean value that when set to ``True``, this module has learnable affine parameters. Default: ``True``.

    Examples::
        >>> m = BNReLU(32, True)
        >>> input = torch.randn(2, 32, 10, 3)
        >>> output = m(input)
    """
    def __init__(self, in_channels: int, affine: bool = True) -> None:
        super(BNReLU, self).__init__()
        self.bn = nn.BatchNorm2d(in_channels, affine = affine)

    def forward(self, input: Tensor) -> Tensor:
        return F.relu(self.bn(input))
