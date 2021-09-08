from typing import Optional

import torch

from .base_modules import Embedding, LayerNorm


class Embeddings(torch.nn.Module):
    def __init__(self, vocab_size: int, dim: int, padding_idx: int, max_position_embeddings: int):
        super().__init__()
        self.word_embeddings = Embedding(vocab_size, dim, padding_idx=padding_idx)
        self.position_embeddings = Embedding(max_position_embeddings, dim)
        self.LayerNorm = LayerNorm(dim)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        embeddings = self.word_embeddings(input_ids) + self.position_embeddings.weight[:input_ids.shape[1]]
        return self.LayerNorm(embeddings)


class MaskEmbeddings(Embeddings):
    def __init__(self, vocab_size: int, dim: int, padding_idx: int, max_position_embeddings: int):
        super().__init__(vocab_size, dim, padding_idx, max_position_embeddings)
        self.padding_idx = padding_idx

    @staticmethod
    def create_position_ids_from_input_ids(input_ids: torch.Tensor, padding_idx: int) -> torch.Tensor:
        mask = input_ids.ne(padding_idx)
        return torch.cumsum(mask, dim=1) * mask + padding_idx

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        position_ids = self.create_position_ids_from_input_ids(input_ids, self.padding_idx)
        embedded = self.word_embeddings(input_ids) + self.position_embeddings(position_ids)
        return self.LayerNorm(embedded)


class EmbeddingsWithTokenTypes(torch.nn.Module):
    def __init__(
            self, vocab_size: int, token_types: int, embedding_size: int, pad_token_id: int,
            max_position_embeddings: int
    ):
        super().__init__()
        self.word_embeddings = Embedding(vocab_size, embedding_size, padding_idx=pad_token_id)
        self.position_embeddings = Embedding(max_position_embeddings, embedding_size)
        self.token_type_embeddings = Embedding(token_types, embedding_size)
        self.LayerNorm = LayerNorm(embedding_size)

    def forward(self, input_ids: torch.Tensor, token_type_ids: Optional[torch.Tensor]) -> torch.Tensor:
        embeddings = self.word_embeddings(input_ids) + self.position_embeddings.weight[:input_ids.shape[1]] + (
            self.token_type_embeddings.weight[0] if token_type_ids is None
            else self.token_type_embeddings(token_type_ids))
        return self.LayerNorm(embeddings)
