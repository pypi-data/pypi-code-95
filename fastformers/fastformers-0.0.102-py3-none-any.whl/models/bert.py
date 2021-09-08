import os
import torch

from ..modules import TransformerEncoder, MaskEmbeddings


class BertModel(torch.nn.Module):
    def __init__(
            self, vocab_size: int, dim: int, padding_idx: int,
            max_position_embeddings: int, ffn_size: int, n_heads: int, n_layers: int):
        super().__init__()

        self.embeddings = MaskEmbeddings(
            vocab_size=vocab_size, dim=dim, padding_idx=padding_idx,
            max_position_embeddings=max_position_embeddings
        )
        self.encoder = TransformerEncoder(
            n_heads=n_heads, embedding_size=dim, ffn_size=ffn_size, n_layers=n_layers)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        embedding_output = self.embeddings(input_ids=input_ids)
        return self.encoder.forward(embedding_output, attention_mask.to(torch.bool))

    @classmethod
    def from_pretrained(cls, model_path: str) -> 'BertModel':
        model = cls(
            vocab_size=28996, dim=1024, padding_idx=0, max_position_embeddings=512,
            ffn_size=4096, n_heads=16, n_layers=24
        )
        model.load_state_dict(state_dict=torch.load(os.path.join(model_path, 'pytorch_model.bin'), map_location='cpu'))
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model.half()
