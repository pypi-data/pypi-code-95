from typing import Optional, Union, Tuple

import torch


class Linear(torch.nn.Linear):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        torch.nn.Module.__init__(self)
        self.in_features = in_features
        self.out_features = out_features
        self.weight = torch.nn.Parameter(torch.empty(out_features, in_features, dtype=torch.float))
        if bias:
            self.bias = torch.nn.Parameter(torch.empty(out_features, dtype=torch.float))
        else:
            self.register_parameter('bias', None)


class Embedding(torch.nn.Embedding):
    def __init__(self, num_embeddings: int, embedding_dim: int, padding_idx: Optional[int] = None):
        torch.nn.Module.__init__(self)
        self.weight = torch.nn.Parameter(torch.empty(num_embeddings, embedding_dim, dtype=torch.float))
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        if padding_idx is not None:
            if padding_idx > 0:
                assert padding_idx < self.num_embeddings, 'Padding_idx must be within num_embeddings'
            elif padding_idx < 0:
                assert padding_idx >= -self.num_embeddings, 'Padding_idx must be within num_embeddings'
                padding_idx += self.num_embeddings
        self.padding_idx = padding_idx
        self.max_norm = None
        self.norm_type = 2.
        self.scale_grad_by_freq = False
        self.sparse = False


class LayerNorm(torch.nn.LayerNorm):
    def __init__(
            self, normalized_shape: Union[int, Tuple[int, ...]], eps: float = 1e-5, elementwise_affine: bool = True
    ):
        torch.nn.Module.__init__(self)
        self.normalized_shape = (normalized_shape,) if isinstance(normalized_shape, int) else normalized_shape
        self.eps = eps
        self.elementwise_affine = elementwise_affine
        if elementwise_affine:
            self.weight = torch.nn.Parameter(torch.empty(normalized_shape, dtype=torch.float))
            self.bias = torch.nn.Parameter(torch.empty(normalized_shape, dtype=torch.float))
        else:
            self.register_parameter('weight', None)
            self.register_parameter('bias', None)
