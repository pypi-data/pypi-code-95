from typing import List

import torch


def neg_inf(fp16: bool) -> float:
    return -65504. if fp16 else -1e20


def transposed_cat(tensors: List[torch.Tensor]) -> torch.Tensor:
    return torch.stack(tensors, dim=1).flatten(0, 1)
