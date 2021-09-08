import os

import torch
from torch import Tensor
from torch.nn import Module

from ..modules import Linear, LayerNorm, Embedding, TransformerEncoder, TransformerDecoder, TanhHead
from ..utils import transposed_cat


class BartModel(Module):
    def __init__(
            self, vocab_size: int, padding_idx: int, eos_token_id: int, dim: int, max_position_embeddings: int,
            encoder_layers: int, encoder_heads: int, encoder_ffn_dim: int,
            decoder_layers: int, decoder_heads: int, decoder_ffn_dim: int
    ):
        super().__init__()

        self.embeddings = Embedding(vocab_size, dim, padding_idx)

        self.encoder_positions = Embedding(
            num_embeddings=max_position_embeddings, embedding_dim=dim, padding_idx=padding_idx)

        self.encoder_norm = LayerNorm(dim)

        self.encoder = TransformerEncoder(
            n_heads=encoder_heads, n_layers=encoder_layers, embedding_size=dim, ffn_size=encoder_ffn_dim)

        self.pre_decoder_layer = Linear(dim, 2 * dim * decoder_layers)

        self.decoder_positions = Embedding(
            num_embeddings=max_position_embeddings, embedding_dim=dim, padding_idx=padding_idx)

        self.decoder_norm = LayerNorm(dim)

        self.encoder_heads = encoder_heads
        self.decoder_layers = decoder_layers

        self.decoder = TransformerDecoder(
            n_heads=decoder_heads, n_layers=decoder_layers, embedding_size=dim, ffn_size=decoder_ffn_dim)

        self.eos_token_id = eos_token_id

    def forward(self, input_ids: Tensor, attention_mask: Tensor):
        attention_mask = attention_mask.to(torch.bool)
        decoder_input_ids = torch.cat(
            [torch.empty((input_ids.shape[0], 1), dtype=torch.long, device=input_ids.device).fill_(self.eos_token_id),
             input_ids[:, :-1]], dim=1)
        decoder_padding_mask = torch.cat(
            [torch.ones((input_ids.shape[0], 1), dtype=torch.bool, device=input_ids.device), attention_mask[:, :-1]],
            dim=1)

        x = self.embeddings(input_ids) + self.encoder_positions.weight[:input_ids.shape[1]]
        x = self.encoder_norm(x)

        encoder_outputs = self.encoder(x, attention_mask)
        encoder_outputs = self.pre_decoder_layer(encoder_outputs)
        encoder_outputs = encoder_outputs.view(
            encoder_outputs.shape[:2] + (self.decoder_layers, 2, self.encoder_heads, -1)).transpose(1, 4).contiguous()

        x = self.embeddings(decoder_input_ids) + self.decoder_positions.weight[:input_ids.shape[1]]
        x = self.decoder_norm(x)

        return self.decoder(
            tensor=x, decoder_mask=decoder_padding_mask, encoder_state=encoder_outputs, encoder_mask=attention_mask
        )[0]


class BartForSequenceClassification(Module):
    def __init__(
            self, vocab_size: int, padding_idx: int, dim: int, max_position_embeddings: int,
            encoder_layers: int, encoder_heads: int, encoder_ffn_dim: int,
            decoder_layers: int, decoder_heads: int, decoder_ffn_dim: int, eos_token_id: int, num_labels: int
    ):
        super().__init__()
        self.transformer = BartModel(
            vocab_size=vocab_size, padding_idx=padding_idx, eos_token_id=eos_token_id, dim=dim,
            max_position_embeddings=max_position_embeddings, encoder_layers=encoder_layers,
            encoder_heads=encoder_heads, encoder_ffn_dim=encoder_ffn_dim, decoder_layers=decoder_layers,
            decoder_heads=decoder_heads, decoder_ffn_dim=decoder_ffn_dim
        )
        self.classification_head = TanhHead(dim, dim, num_labels)

        self.eos_token_id = eos_token_id

    def replace_encoder_keys(self, state_dict: dict):
        encoder_old_names = {
            'attention.out_lin': 'self_attn.out_proj',
            'norm1': 'self_attn_layer_norm',
            'norm2': 'final_layer_norm',
            'ffn.lin1': 'fc1',
            'ffn.lin2': 'fc2'
        }

        for layer_ind in range(len(self.transformer.encoder.layers)):
            prefix = f'model.encoder.layers.{layer_ind}.'
            for w in ('weight', 'bias'):
                state_dict[f'{prefix}attention.pre_attention.{w}'] = transposed_cat([
                    state_dict.pop(f'{prefix}self_attn.{k}_proj.{w}') for k in ('q', 'k', 'v')
                ])
                for new_name, old_name in encoder_old_names.items():
                    state_dict[f'{prefix}{new_name}.{w}'] = state_dict.pop(f'{prefix}{old_name}.{w}')

    def replace_decoder_keys(self, state_dict: dict):
        decoder_old_names = {
            'encoder_attention.q_lin': 'encoder_attn.q_proj',
            'encoder_attention.out_lin': 'encoder_attn.out_proj',
            'self_attention.out_lin': 'self_attn.out_proj',
            'ffn.lin1': 'fc1',
            'ffn.lin2': 'fc2',
            'norm1': 'self_attn_layer_norm',
            'norm2': 'encoder_attn_layer_norm',
            'norm3': 'final_layer_norm'
        }

        for layer_ind in range(len(self.transformer.decoder.layers)):
            prefix = f'model.decoder.layers.{layer_ind}.'
            for w in ('weight', 'bias'):
                state_dict[f'{prefix}self_attention.pre_attention.{w}'] = transposed_cat([
                    state_dict.pop(f'{prefix}self_attn.{k}_proj.{w}') for k in ('q', 'k', 'v')
                ])
                for new_name, old_name in decoder_old_names.items():
                    state_dict[f'{prefix}{new_name}.{w}'] = state_dict.pop(f'{prefix}{old_name}.{w}')

    def load_state_dict(self, state_dict, strict: bool = True):
        keys_to_delete = [
            'model.encoder.version', 'model.decoder.version', 'model.encoder.embed_tokens.weight',
            'model.decoder.embed_tokens.weight']
        for key in keys_to_delete:
            state_dict.pop(key, None)
        old_names = {
            'model.encoder_positions.weight': 'model.encoder.embed_positions.weight',
            'model.encoder_norm.weight': 'model.encoder.layernorm_embedding.weight',
            'model.encoder_norm.bias': 'model.encoder.layernorm_embedding.bias',
            'model.decoder_positions.weight': 'model.decoder.embed_positions.weight',
            'model.decoder_norm.weight': 'model.decoder.layernorm_embedding.weight',
            'model.decoder_norm.bias': 'model.decoder.layernorm_embedding.bias'
        }

        for new_name, old_name in old_names.items():
            state_dict[new_name] = state_dict.pop(old_name)

        state_dict['model.encoder_positions.weight'] = state_dict['model.encoder_positions.weight'][2:]
        state_dict['model.decoder_positions.weight'] = state_dict['model.decoder_positions.weight'][2:]

        for p in ('weight', 'bias'):
            state_dict[f'model.pre_decoder_layer.{p}'] = torch.cat(
                [state_dict.pop(f'model.decoder.layers.{ind}.encoder_attn.{name}_proj.{p}')
                 for ind in range(len(self.transformer.decoder.layers)) for name in 'kv'], dim=0)

        self.replace_encoder_keys(state_dict)
        self.replace_decoder_keys(state_dict)

        module_names = {'embeddings': 'shared', 'transformer': 'model'}
        for key, value in list(state_dict.items()):
            new_key = key
            for name, old_name in module_names.items():
                new_key = new_key.replace(f'{old_name}.', f'{name}.')
            state_dict[new_key] = state_dict.pop(key)

        super().load_state_dict(state_dict, strict)

    @classmethod
    def from_pretrained(cls, model_path: str, decoder_layers: int = 12) -> 'BartForSequenceClassification':
        model = cls(
            vocab_size=50265, padding_idx=1, dim=1024, max_position_embeddings=1024,
            encoder_layers=12, encoder_heads=16, encoder_ffn_dim=4096,
            decoder_layers=decoder_layers, decoder_heads=16, decoder_ffn_dim=4096, num_labels=3, eos_token_id=2
        )
        model.load_state_dict(state_dict=torch.load(os.path.join(model_path, 'pytorch_model.bin'), map_location='cpu'))
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model.half()

    def forward(self, input_ids: Tensor, attention_mask: Tensor) -> Tensor:
        tensor = self.transformer(input_ids, attention_mask=attention_mask)
        eos_mask = input_ids.eq(self.eos_token_id)
        bsz, _, dim = tensor.shape
        tensor = tensor[eos_mask].view(bsz, -1, dim)[:, -1]
        return self.classification_head(tensor)
