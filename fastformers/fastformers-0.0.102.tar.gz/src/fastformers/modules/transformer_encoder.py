import torch
from torch.nn import Module, ModuleList

from .base_modules import LayerNorm
from .attention import MultiHeadAttention
from .feed_forward import TransformerFFN


class TransformerEncoderLayer(Module):
    def __init__(self, n_heads: int, embedding_size: int, ffn_size: int, blender_norm: bool):
        super().__init__()
        self.attention = MultiHeadAttention(n_heads, embedding_size)
        self.norm1 = LayerNorm(embedding_size)

        self.ffn = TransformerFFN(embedding_size, ffn_size)
        self.norm2 = LayerNorm(embedding_size)

        self.blender_norm = blender_norm

    def forward(self, tensor: torch.Tensor, mask: torch.Tensor):
        residual = tensor
        if self.blender_norm:
            tensor = self.norm1(tensor)
        tensor = self.attention(tensor, mask=mask)[0]
        tensor = tensor + residual
        if not self.blender_norm:
            tensor = self.norm1(tensor)
        residual = tensor
        if self.blender_norm:
            tensor = self.norm2(tensor)
        tensor = self.ffn(tensor)
        tensor = tensor + residual
        if not self.blender_norm:
            tensor = self.norm2(tensor)
        return tensor


class TransformerEncoder(Module):
    def __init__(self, n_heads: int, n_layers: int, embedding_size: int, ffn_size: int, blender_norm: bool = False):
        super(TransformerEncoder, self).__init__()

        self.layers = ModuleList(
            TransformerEncoderLayer(n_heads, embedding_size, ffn_size, blender_norm) for _ in range(n_layers))
        self.n_heads = n_heads

    def forward(self, tensor: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        attn_mask = ~mask.repeat_interleave(repeats=self.n_heads, dim=0).unsqueeze(1).expand(-1, mask.shape[1], -1)

        for layer in self.layers:
            tensor = layer.forward(tensor, attn_mask)

        return tensor * mask.unsqueeze(-1)
