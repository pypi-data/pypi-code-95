import torch

from .time_distributed import TimeDistributed
from .coref_utils import batched_index_select, batched_span_select, masked_softmax, weighted_sum


class SpanExtractor(torch.nn.Module):
    def __init__(self, num_width_embeddings: int, span_width_embedding_dim: int):
        super().__init__()

        self._span_width_embedding = torch.nn.Embedding(
            num_embeddings=num_width_embeddings, embedding_dim=span_width_embedding_dim)

    def forward(self, sequence_tensor: torch.Tensor, span_indices: torch.Tensor) -> torch.Tensor:
        span_starts, span_ends = [index.squeeze(-1) for index in span_indices.split(1, dim=-1)]

        start_embeddings = batched_index_select(sequence_tensor, span_starts)
        end_embeddings = batched_index_select(sequence_tensor, span_ends)
        span_width_embeddings = self._span_width_embedding(span_ends - span_starts)
        return torch.cat([start_embeddings, end_embeddings, span_width_embeddings], -1)


class SelfAttentiveSpanExtractor(torch.nn.Module):
    def __init__(self, input_dim: int) -> None:
        super().__init__()
        self._global_attention = TimeDistributed(torch.nn.Linear(input_dim, 1))

    def forward(self, sequence_tensor: torch.Tensor, span_indices: torch.Tensor) -> torch.Tensor:
        # shape (batch_size, sequence_length, 1)
        global_attention_logits = self._global_attention(sequence_tensor)

        # shape (batch_size, sequence_length, embedding_dim + 1)
        concat_tensor = torch.cat([sequence_tensor, global_attention_logits], -1)

        concat_output, span_mask = batched_span_select(concat_tensor, span_indices)

        # Shape: (batch_size, num_spans, max_batch_span_width, embedding_dim)
        span_embeddings = concat_output[:, :, :, :-1]
        # Shape: (batch_size, num_spans, max_batch_span_width)
        span_attention_logits = concat_output[:, :, :, -1]

        # Shape: (batch_size, num_spans, max_batch_span_width)
        span_attention_weights = masked_softmax(span_attention_logits, span_mask)

        # Do a weighted sum of the embedded spans with
        # respect to the normalised attention distributions.
        # Shape: (batch_size, num_spans, embedding_dim)
        return weighted_sum(span_embeddings, span_attention_weights)
