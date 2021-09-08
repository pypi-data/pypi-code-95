from typing import Optional

import os
import logging

import torch
from torch import Tensor
from torch.nn import Module
from torch.nn.functional import gelu

from ..modules import Linear, TransformerEncoder, EmbeddingsWithTokenTypes
from ..utils import transposed_cat


logger = logging.getLogger(__name__)


class ElectraModel(Module):
    def __init__(
            self, vocab_size: int, token_types: int, dim: int, pad_token_id: int,
            max_position_embeddings: int, ffn_size: int, n_heads: int, n_layers: int
    ):
        super().__init__()
        self.embeddings = EmbeddingsWithTokenTypes(
            vocab_size=vocab_size, token_types=token_types, embedding_size=dim, pad_token_id=pad_token_id,
            max_position_embeddings=max_position_embeddings
        )

        self.encoder = TransformerEncoder(
            n_heads=n_heads, embedding_size=dim, ffn_size=ffn_size, n_layers=n_layers)

    def forward(self, input_ids: Tensor, attention_mask: Tensor, token_type_ids: Optional[Tensor]) -> Tensor:
        hidden_states = self.embeddings(input_ids=input_ids, token_type_ids=token_type_ids)
        return self.encoder(hidden_states, mask=attention_mask.to(torch.bool))


class ElectraClassificationHead(Module):
    """Head for sentence-level classification tasks."""

    def __init__(self, dim: int, num_labels: int):
        super().__init__()
        self.dense = Linear(dim, dim)
        self.out_proj = Linear(dim, num_labels)

    def forward(self, features):
        x = features[:, 0]
        x = self.dense(x)
        x = gelu(x)
        x = self.out_proj(x)
        return x


class ElectraForSequenceClassification(Module):
    def __init__(
            self, vocab_size: int, token_types: int, dim: int, pad_token_id: int,
            max_position_embeddings: int, ffn_size: int, n_heads: int, n_layers: int,
            num_labels: int, activation: str
    ):
        super().__init__()

        self.num_labels = num_labels
        self.transformer = ElectraModel(
            vocab_size=vocab_size, token_types=token_types, dim=dim, pad_token_id=pad_token_id,
            max_position_embeddings=max_position_embeddings, ffn_size=ffn_size, n_heads=n_heads, n_layers=n_layers)
        self.classifier = ElectraClassificationHead(dim, num_labels)
        self.sigmoid = True if activation == 'sigmoid' else False

    def forward(self, input_ids: Tensor, attention_mask: Tensor, token_type_ids: Optional[Tensor] = None):
        tensor = self.transformer(input_ids, attention_mask, token_type_ids)
        tensor = self.classifier(tensor)
        return tensor.sigmoid() if self.sigmoid else tensor.softmax(dim=-1)

    @classmethod
    def from_pretrained(cls, model_path: str, num_labels: int, activation: str) -> 'ElectraForSequenceClassification':
        model = cls(
            vocab_size=30522, token_types=2, dim=768, pad_token_id=0, max_position_embeddings=512,
            ffn_size=3072, n_heads=12, n_layers=12, num_labels=num_labels, activation=activation
        )
        model.load_state_dict(state_dict=torch.load(os.path.join(model_path, 'pytorch_model.bin'), map_location='cpu'))
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model.half()

    def load_state_dict(self, state_dict, strict=True):
        del state_dict['electra.embeddings.position_ids']
        module_names = {'layers': 'layer', 'transformer': 'electra'}
        for key, value in list(state_dict.items()):
            new_key = key
            for name, old_name in module_names.items():
                new_key = new_key.replace(f'{old_name}.', f'{name}.')
            state_dict[new_key] = state_dict.pop(key)
        old_names = {
            'attention.out_lin': 'attention.output.dense',
            'norm1': 'attention.output.LayerNorm',
            'norm2': 'output.LayerNorm',
            'ffn.lin1': 'intermediate.dense',
            'ffn.lin2': 'output.dense'
        }
        for layer_ind in range(len(self.transformer.encoder.layers)):
            prefix = f'transformer.encoder.layers.{layer_ind}.'
            for p in ('weight', 'bias'):
                state_dict[f'{prefix}attention.pre_attention.{p}'] = transposed_cat([
                    state_dict.pop(f'{prefix}attention.self.{k}.{p}') for k in ('query', 'key', 'value')
                ])
                for new_name, old_name in old_names.items():
                    state_dict[f'{prefix}{new_name}.{p}'] = state_dict.pop(f'{prefix}{old_name}.{p}')
        return super().load_state_dict(state_dict, strict)
