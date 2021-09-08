from typing import Optional, Tuple, List

import torch
from torch.nn import Module, ModuleList

from .base_modules import LayerNorm
from .attention import MultiHeadAttention, DecoderEncoderAttention
from .feed_forward import TransformerFFN


class TransformerDecoderLayer(Module):
    def __init__(self, n_heads: int, embedding_size: int, ffn_size: int, blender_norm: bool):
        super().__init__()
        self.dim = embedding_size

        self.self_attention = MultiHeadAttention(n_heads, embedding_size)
        self.norm1 = LayerNorm(embedding_size)

        self.encoder_attention = DecoderEncoderAttention(n_heads, embedding_size)
        self.norm2 = LayerNorm(embedding_size)

        self.ffn = TransformerFFN(embedding_size, ffn_size)
        self.norm3 = LayerNorm(embedding_size)

        self.blender_norm = blender_norm

    def forward(
            self, tensor, decoder_mask: torch.Tensor, encoder_state: torch.Tensor, encoder_mask: torch.Tensor,
            incr_state: Optional[torch.Tensor] = None, get_incr_state: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        residual = tensor
        if self.blender_norm:
            tensor = self.norm1(tensor)
        tensor, incr_state = self.self_attention(
            query=tensor, mask=decoder_mask, incr_state=incr_state, get_incr_state=get_incr_state)
        tensor = tensor + residual
        if not self.blender_norm:
            tensor = self.norm1(tensor)
        residual = tensor
        if self.blender_norm:
            tensor = self.norm2(tensor)
        tensor = self.encoder_attention(
            query=tensor, key=encoder_state[:, 0], value=encoder_state[:, 1], mask=encoder_mask)
        tensor = tensor + residual
        if not self.blender_norm:
            tensor = self.norm2(tensor)
        residual = tensor
        if self.blender_norm:
            tensor = self.norm3(tensor)
        tensor = self.ffn(tensor)
        tensor = residual + tensor
        if not self.blender_norm:
            tensor = self.norm3(tensor)
        return tensor, incr_state


class TransformerDecoder(Module):
    def __init__(self, n_heads: int, n_layers: int, embedding_size: int, ffn_size: int, blender_norm: bool = False):
        super().__init__()

        self.layers = ModuleList(
            TransformerDecoderLayer(n_heads, embedding_size, ffn_size, blender_norm) for _ in range(n_layers))
        self.n_heads = n_heads

    def process_decoder_mask(self, decoder_mask: torch.Tensor, decoder_length: int) -> torch.Tensor:
        bsz, seq_len = decoder_mask.shape
        mask = torch.tril(torch.ones(seq_len, seq_len, dtype=torch.bool, device=decoder_mask.device))
        mask = mask.unsqueeze(0)[:, -decoder_length:] & decoder_mask.unsqueeze(1)
        return ~mask.repeat_interleave(repeats=self.n_heads, dim=0).expand(-1, decoder_length, -1)

    def forward(
            self, tensor: torch.Tensor, decoder_mask: torch.Tensor,
            encoder_mask: torch.Tensor, encoder_state: torch.Tensor,
            incr_state: Optional[torch.Tensor] = None, get_incr_state: bool = True
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:

        decoder_length = tensor.shape[1]
        decoder_mask = self.process_decoder_mask(decoder_mask, decoder_length=decoder_length)
        encoder_mask = ~encoder_mask.repeat_interleave(
            repeats=self.n_heads, dim=0).unsqueeze(1).expand(-1, decoder_length, -1)

        encoder_state = encoder_state.flatten(0, 1)

        new_incr_states: List[torch.Tensor] = []
        for ind, layer in enumerate(self.layers):
            tensor, new_layer_state = layer.forward(
                tensor=tensor,
                decoder_mask=decoder_mask,
                encoder_state=encoder_state[:, ind],
                encoder_mask=encoder_mask,
                incr_state=incr_state[:, :, :, :, ind] if incr_state is not None else None,
                get_incr_state=get_incr_state
            )
            if get_incr_state:
                assert new_layer_state is not None
                new_incr_states.append(new_layer_state)

        return tensor, torch.stack(new_incr_states, dim=-1) if get_incr_state else None
