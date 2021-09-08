import os
import logging

import torch
from torch.nn import Module
from torch.nn.functional import gelu

from ..modules import LayerNorm, Linear, TransformerEncoder, Embeddings
from ..utils import transposed_cat


logger = logging.getLogger(__name__)


class DistilBertModel(torch.nn.Module):
    def __init__(
            self, vocab_size: int, dim: int, padding_idx: int, max_position_embeddings: int, ffn_size: int,
            n_heads: int, n_layers: int
    ):
        super().__init__()

        self.embeddings = Embeddings(
            vocab_size=vocab_size, dim=dim, padding_idx=padding_idx,
            max_position_embeddings=max_position_embeddings)
        self.encoder = TransformerEncoder(
            n_heads=n_heads, n_layers=n_layers, embedding_size=dim, ffn_size=ffn_size)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        inputs_embeds = self.embeddings(input_ids)
        return self.encoder(inputs_embeds, attention_mask)


class DistilBertForMaskedLM(Module):
    def __init__(
            self, vocab_size: int, dim: int, padding_idx: int, max_position_embeddings: int, ffn_size: int,
            n_heads: int, n_layers: int, mask_token_id: int
    ):
        super().__init__()

        self.transformer = DistilBertModel(
            vocab_size=vocab_size, dim=dim, padding_idx=padding_idx, max_position_embeddings=max_position_embeddings,
            n_heads=n_heads, n_layers=n_layers, ffn_size=ffn_size
        )
        self.vocab_transform = Linear(dim, dim)
        self.vocab_layer_norm = LayerNorm(dim)
        self.vocab_projector = Linear(dim, vocab_size)

        self.mask_token_id = mask_token_id

    @classmethod
    def from_pretrained(cls, model_path: str) -> 'DistilBertForMaskedLM':
        model = cls(
            vocab_size=28996, dim=768, padding_idx=0, max_position_embeddings=512, ffn_size=3072, n_heads=12,
            n_layers=6, mask_token_id=103
        )
        model.load_state_dict(state_dict=torch.load(os.path.join(model_path, 'pytorch_model.bin'), map_location='cpu'))
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model.half()

    def load_state_dict(self, state_dict, strict=True):
        module_names = {'layers': 'layer', 'encoder': 'transformer', 'transformer': 'distilbert'}
        for key, value in list(state_dict.items()):
            new_key = key
            for name, old_name in module_names.items():
                new_key = new_key.replace(f'{old_name}.', f'{name}.')
            state_dict[new_key] = state_dict.pop(key)
        for layer_ind in range(len(self.transformer.encoder.layers)):
            prefix = f'transformer.encoder.layers.{layer_ind}.'
            for p in ('weight', 'bias'):
                state_dict[f'{prefix}attention.pre_attention.{p}'] = transposed_cat([
                    state_dict.pop(f'{prefix}attention.{k}_lin.{p}') for k in ('q', 'k', 'v')
                ])
                state_dict[f'{prefix}norm1.{p}'] = state_dict.pop(f'{prefix}sa_layer_norm.{p}')
                state_dict[f'{prefix}norm2.{p}'] = state_dict.pop(f'{prefix}output_layer_norm.{p}')
        return super().load_state_dict(state_dict, strict)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        hidden_states = self.transformer(input_ids=input_ids, attention_mask=attention_mask.to(torch.bool))
        prediction_logits = self.vocab_transform(hidden_states)
        prediction_logits = gelu(prediction_logits)
        prediction_logits = self.vocab_layer_norm(prediction_logits)
        prediction_logits = self.vocab_projector(prediction_logits)
        mask_indices = torch.nonzero(input_ids == self.mask_token_id, as_tuple=True)[1]
        mask_indices = mask_indices.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, prediction_logits.shape[-1])
        return prediction_logits.gather(dim=1, index=mask_indices)[:, 0].softmax(dim=-1).gather(dim=-1, index=targets)
