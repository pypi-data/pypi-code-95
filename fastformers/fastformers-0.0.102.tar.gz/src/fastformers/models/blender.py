from typing import Optional, Tuple

import math

import torch
from torch.nn.functional import linear
import torch.jit

from ..modules import Linear, LayerNorm, Embedding, TransformerEncoder, TransformerDecoder
from ..utils import transposed_cat


class Blender(torch.nn.Module):
    def __init__(
            self, vocabulary_size: int, dim: int, n_positions: int, n_heads: int, ffn_size: int,
            n_encoder_layers: int, n_decoder_layers: int, num_labels: int
    ):
        super().__init__()
        self.embeddings = Embedding(vocabulary_size, dim, 0)
        self.position_embeddings = Embedding(n_positions, dim)

        self.encoder_norm = LayerNorm(dim)
        self.encoder = self.build_encoder(
            n_heads=n_heads, n_encoder_layers=n_encoder_layers, dim=dim, ffn_size=ffn_size
        )

        self.pre_decoder_layer = Linear(dim, 2 * dim * n_decoder_layers)

        self.decoder_norm = LayerNorm(dim)
        self.decoder = self.build_decoder(
            n_heads=n_heads, n_decoder_layers=n_decoder_layers, embedding_size=dim, ffn_size=ffn_size
        )

        self.classifier_head = torch.nn.Linear(dim, num_labels) if num_labels else None
        self.scale = math.sqrt(dim)

        self.n_decoder_layers = n_decoder_layers
        self.n_heads = n_heads

    @classmethod
    def from_pretrained(
            cls, model_path: str, vocabulary_size: int, embedding_size: int, n_positions: int, n_heads: int,
            ffn_size: int, n_encoder_layers: int, n_decoder_layers: int, num_labels: int
    ):
        model = cls(
            vocabulary_size=vocabulary_size, dim=embedding_size,
            n_positions=n_positions, n_heads=n_heads, ffn_size=ffn_size,
            n_encoder_layers=n_encoder_layers, n_decoder_layers=n_decoder_layers,
            num_labels=num_labels
        )
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model = model

        model.eval()

        for param in model.parameters():
            param.requires_grad = False

        return model.half()

    def embedding_forward(self, tensor: torch.Tensor, positions: torch.Tensor) -> torch.Tensor:
        return self.embeddings(tensor) * self.scale + self.position_embeddings(positions)

    @torch.jit.export
    def encode(self, encoder_ids: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        mask = encoder_ids.to(torch.bool)
        positions = (mask.cumsum(dim=1, dtype=torch.long) - 1).clamp_(min=0)
        tensor = self.embedding_forward(encoder_ids, positions)
        tensor = self.encoder.forward(tensor, mask)
        tensor = self.encoder_norm(tensor)
        tensor = self.pre_decoder_layer(tensor).view(
            tensor.shape[:2] + (self.n_decoder_layers, 2, self.n_heads, -1)).transpose(1, 4).contiguous()
        return tensor, mask

    @torch.jit.export
    def decode(
            self, decoder_ids: torch.Tensor, encoder_state: torch.Tensor, encoder_mask: torch.Tensor,
            incr_state: Optional[torch.Tensor], get_incr_state: bool
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        mask = decoder_ids.to(torch.bool)

        positions = mask.cumsum(dim=1, dtype=torch.long)
        if incr_state is not None:
            decode_step = decoder_ids.shape[1] - incr_state.shape[2]
            incr_state = incr_state.flatten(0, 1)
            decoder_ids = decoder_ids[:, -decode_step:]
            positions = positions[:, -decode_step:]

        positions = (positions - 1).clamp_(min=0)

        tensor = self.embedding_forward(decoder_ids, positions)

        tensor, incr_state = self.decoder.forward(
            tensor=tensor, decoder_mask=mask, encoder_state=encoder_state, encoder_mask=encoder_mask,
            incr_state=incr_state, get_incr_state=get_incr_state
        )
        tensor = self.decoder_norm(tensor)
        return tensor, incr_state

    @classmethod
    def build_decoder(cls, n_heads, n_decoder_layers, embedding_size, ffn_size):
        return TransformerDecoder(
            n_heads=n_heads, n_layers=n_decoder_layers, embedding_size=embedding_size, ffn_size=ffn_size,
            blender_norm=True
        )

    @classmethod
    def build_encoder(cls, n_heads, n_encoder_layers, dim, ffn_size):
        return TransformerEncoder(
            n_heads=n_heads, n_layers=n_encoder_layers, embedding_size=dim, ffn_size=ffn_size, blender_norm=True
        )

    @classmethod
    def convert_old_state_dict(cls, state_dict: dict, n_encoder_layers: int, n_decoder_layers: int):
        for p in 'weight', 'bias':
            for module in 'encoder', 'decoder':
                state_dict[f'{module}_norm.{p}'] = state_dict.pop(f'{module}.norm_embeddings.{p}')
            state_dict[f'pre_decoder_layer.{p}'] = torch.cat(
                [state_dict.pop(f'decoder.layers.{ind}.encoder_attention.{name}_lin.{p}')
                 for ind in range(n_decoder_layers) for name in 'kv'], dim=0)
            for ind in range(n_encoder_layers):
                state_dict[f'encoder.layers.{ind}.attention.pre_attention.{p}'] = transposed_cat(
                    [state_dict.pop(f'encoder.layers.{ind}.attention.{name}_lin.{p}') for name in 'qkv'])
            for ind in range(n_decoder_layers):
                state_dict[f'decoder.layers.{ind}.self_attention.pre_attention.{p}'] = transposed_cat(
                    [state_dict.pop(f'decoder.layers.{ind}.self_attention.{name}_lin.{p}') for name in 'qkv'])

        state_dict['position_embeddings.weight'] = state_dict['encoder.position_embeddings.weight']

        keys_to_delete = [
            'criterion.weight', 'START',
            'encoder.embeddings.weight', 'encoder.position_embeddings.weight',
            'decoder.embeddings.weight', 'decoder.position_embeddings.weight'
        ]

        for key in keys_to_delete:
            state_dict.pop(key, None)

    def load_state_dict(self, state_dict: dict, strict=True):
        if 'model' in state_dict:
            state_dict = state_dict['model']

        if self.classifier_head is None:
            for p in ('weight', 'bias'):
                state_dict.pop(f'classifier_head.{p}', None)

        if 'encoder.pre_decoder_layer.weight' not in state_dict:
            self.convert_old_state_dict(
                state_dict, n_encoder_layers=len(self.encoder.layers), n_decoder_layers=len(self.decoder.layers))

        super().load_state_dict(state_dict, strict)

    @torch.jit.export
    def output(self, tensor: torch.Tensor) -> torch.Tensor:
        return linear(tensor, self.embeddings.weight)
