import os
import logging

import torch

from ..modules import Linear, TransformerEncoder, MaskEmbeddings
from ..utils import transposed_cat, neg_inf


logger = logging.getLogger(__name__)


class RobertaModel(torch.nn.Module):
    def __init__(
            self, vocab_size: int, dim: int, padding_idx: int, max_position_embeddings: int, ffn_size: int,
            n_heads: int, n_layers: int
    ):
        super().__init__()

        self.embeddings = MaskEmbeddings(
            vocab_size=vocab_size, dim=dim, padding_idx=padding_idx,
            max_position_embeddings=max_position_embeddings
        )
        self.encoder = TransformerEncoder(
            n_heads=n_heads, embedding_size=dim, ffn_size=ffn_size, n_layers=n_layers)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        embedding_output = self.embeddings(input_ids=input_ids)
        return self.encoder.forward(embedding_output, attention_mask)


class RobertaForQuestionAnswering(torch.nn.Module):
    def __init__(
            self, vocab_size: int, dim: int, padding_idx: int,
            max_position_embeddings: int, ffn_size: int, n_heads: int, n_layers: int, num_labels: int):
        super().__init__()
        self.transformer = RobertaModel(
            vocab_size=vocab_size, dim=dim, padding_idx=padding_idx,
            max_position_embeddings=max_position_embeddings, ffn_size=ffn_size, n_heads=n_heads, n_layers=n_layers
        )
        self.qa_outputs = Linear(dim, num_labels)

    @classmethod
    def from_pretrained(cls, model_path: str) -> 'RobertaForQuestionAnswering':
        model = cls(
            vocab_size=50265, dim=768, padding_idx=1, max_position_embeddings=514,
            ffn_size=3072, n_heads=12, n_layers=12, num_labels=2
        )
        model.load_state_dict(state_dict=torch.load(os.path.join(model_path, 'pytorch_model.bin'), map_location='cpu'))
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model.half()

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, answer_mask: torch.Tensor) -> torch.Tensor:
        logits = self.transformer(input_ids, attention_mask=attention_mask)
        logits = self.qa_outputs(logits)
        logits.masked_fill_(~answer_mask.unsqueeze(-1), neg_inf(logits.dtype == torch.float16))
        logits = (logits - logits.exp().sum(dim=1, keepdim=True).log()).exp()
        logits[:, 0] = 0.
        return logits

    def load_state_dict(self, state_dict, strict=True):
        module_names = {'layers': 'layer', 'transformer': 'roberta'}
        for key, value in list(state_dict.items()):
            new_key = key
            for name, old_name in module_names.items():
                new_key = new_key.replace(f'{old_name}.', f'{name}.')
            state_dict[new_key] = state_dict.pop(key)
        del state_dict['transformer.embeddings.position_ids']
        old_names = {
            'attention.out_lin': 'attention.output.dense',
            'norm1': 'attention.output.LayerNorm',
            'norm2': 'output.LayerNorm',
            'ffn.lin1': 'intermediate.dense',
            'ffn.lin2': 'output.dense'
        }
        state_dict['transformer.embeddings.word_embeddings.weight'] += state_dict.pop(
            'transformer.embeddings.token_type_embeddings.weight')
        for layer_ind in range(len(self.transformer.encoder.layers)):
            prefix = f'transformer.encoder.layers.{layer_ind}.'
            for p in ('weight', 'bias'):
                state_dict[f'{prefix}attention.pre_attention.{p}'] = transposed_cat([
                    state_dict.pop(f'{prefix}attention.self.{k}.{p}') for k in ('query', 'key', 'value')
                ])
                for new_name, old_name in old_names.items():
                    state_dict[f'{prefix}{new_name}.{p}'] = state_dict.pop(f'{prefix}{old_name}.{p}')
        return super().load_state_dict(state_dict, strict)
