from typing import Optional, Tuple

import math

import torch
from torch.nn import Module

from .base_modules import Linear
from ..utils import neg_inf


class MultiHeadAttention(Module):
    def __init__(self, n_heads: int, dim: int):
        super().__init__()
        self.pre_attention = Linear(dim, dim * 3)
        self.out_lin = Linear(dim, dim)

        self.n_heads = n_heads
        self.dim_per_head = dim // n_heads
        self.scale = math.sqrt(self.dim_per_head)

    def forward(
            self, query: torch.Tensor, mask: torch.Tensor,
            incr_state: Optional[torch.Tensor] = None, get_incr_state: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch_size, seq_len, dim = query.shape

        query = self.pre_attention(query)
        query = query.view(batch_size, seq_len, self.n_heads, self.dim_per_head, 3)
        query = query.transpose(1, 2).contiguous()
        query = query.view(batch_size * self.n_heads, seq_len, self.dim_per_head, 3)

        q = query[:, :, :, 0] / self.scale
        k_v = query[:, :, :, 1:]

        if incr_state is not None:
            k_v = torch.cat([incr_state, k_v], dim=1)

        incr_state = k_v.view(batch_size, self.n_heads, -1, self.dim_per_head, 2) if get_incr_state else None

        dot_prod = q.bmm(k_v[:, :, :, 0].transpose(1, 2))

        dot_prod.masked_fill_(mask, neg_inf(dot_prod.dtype == torch.float16))

        attn_weights = dot_prod.softmax(dim=-1, dtype=torch.float).type_as(query)

        return self.out_lin(attn_weights.bmm(k_v[:, :, :, 1]).view(
            batch_size, self.n_heads, seq_len,
            self.dim_per_head).transpose(1, 2).contiguous().view(batch_size, seq_len, dim)), incr_state


class DecoderEncoderAttention(Module):
    def __init__(self, n_heads: int, dim: int):
        super().__init__()
        self.q_lin = Linear(dim, dim)
        self.out_lin = Linear(dim, dim)

        self.n_heads = n_heads
        self.dim_per_head = dim // n_heads
        self.scale = math.sqrt(self.dim_per_head)

    def forward(self, query: torch.Tensor, mask: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, dim = query.shape

        query = self.q_lin(query) / self.scale
        query = query.view(batch_size, seq_len, self.n_heads, self.dim_per_head).transpose(1, 2).contiguous()
        query = query.view(batch_size * self.n_heads, seq_len, self.dim_per_head)

        dot_prod = query.bmm(key.transpose(1, 2))

        dot_prod.masked_fill_(mask, neg_inf(dot_prod.dtype == torch.float16))

        attn_weights = dot_prod.softmax(dim=-1, dtype=torch.float).type_as(query)

        return self.out_lin(attn_weights.bmm(value).view(
            batch_size, self.n_heads, seq_len,
            self.dim_per_head).transpose(1, 2).contiguous().view(batch_size, seq_len, dim))
