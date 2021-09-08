import logging
import math
from typing import Tuple

import torch
from torch.nn.functional import pad

from .coref_utils import batched_index_select, batched_span_select
from ..bert import BertModel

logger = logging.getLogger(__name__)


class TransformerEmbedder(torch.nn.Module):
    def __init__(self, max_length: int):
        super().__init__()

        self.model = BertModel(
            vocab_size=28996, dim=1024, padding_idx=0, max_position_embeddings=512, ffn_size=4096, n_heads=16,
            n_layers=24
        )

        self._max_length = max_length

        self.output_dim = 1024

        self._num_added_start_tokens = 1
        self._num_added_end_tokens = 1
        self._num_added_tokens = self._num_added_start_tokens + self._num_added_end_tokens

    def get_output_dim(self):
        return self.output_dim

    def forward(
            self, token_ids: torch.Tensor, offsets: torch.Tensor, segment_concat_mask: torch.Tensor) -> torch.Tensor:
        fold_long_sequences = token_ids.shape[1] > self._max_length
        batch_size, num_segment_concat_wordpieces = token_ids.shape
        if fold_long_sequences:
            token_ids, segment_concat_mask = self._fold_long_sequences(token_ids, segment_concat_mask)

        # Shape: [batch_size, num_wordpieces, embedding_size],
        # or if self._max_length is not None:
        # [batch_size * num_segments, self._max_length, embedding_size]
        embeddings = self.model(input_ids=token_ids, attention_mask=segment_concat_mask)

        if fold_long_sequences:
            embeddings = self._unfold_long_sequences(
                embeddings, segment_concat_mask, batch_size, num_segment_concat_wordpieces)

        span_embeddings, span_mask = batched_span_select(embeddings.contiguous(), offsets)

        span_mask = span_mask.unsqueeze(-1)

        # Shape: (batch_size, num_orig_tokens, max_span_length, embedding_size)
        span_embeddings *= span_mask  # zero out paddings

        # Sum over embeddings of all sub-tokens of a word
        # Shape: (batch_size, num_orig_tokens, embedding_size)
        span_embeddings_sum = span_embeddings.sum(2)

        # Shape (batch_size, num_orig_tokens)
        span_embeddings_len = span_mask.sum(2)

        # Find the average of sub-tokens embeddings by dividing `span_embedding_sum` by `span_embedding_len`
        # Shape: (batch_size, num_orig_tokens, embedding_size)
        orig_embeddings = span_embeddings_sum / torch.clamp_min(span_embeddings_len, 1)

        # All the places where the span length is zero, write in zeros.
        orig_embeddings[(span_embeddings_len == 0).expand(orig_embeddings.shape)] = 0

        return orig_embeddings

    def fold(self, tensor: torch.Tensor, length_to_pad: int) -> torch.Tensor:
        # Shape: [batch_size, num_segments * self._max_length]
        tensor = pad(tensor, [0, length_to_pad], value=0.)
        # Shape: [batch_size * num_segments, self._max_length]
        return tensor.reshape(-1, self._max_length)

    def _fold_long_sequences(self, token_ids: torch.Tensor, mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        We fold 1D sequences (for each element in batch), returned by `PretrainedTransformerIndexer`
        that are in reality multiple segments concatenated together, to 2D tensors, e.g.

        [ [CLS] A B C [SEP] [CLS] D E [SEP] ]
        -> [ [ [CLS] A B C [SEP] ], [ [CLS] D E [SEP] [PAD] ] ]
        The [PAD] positions can be found in the returned `mask`.

        # Parameters

        token_ids: `torch.LongTensor`
            Shape: `[batch_size, num_segment_concat_wordpieces]`.
            num_segment_concat_wordpieces is num_wordpieces plus special tokens inserted in the
            middle, i.e. the length of: "[CLS] A B C [SEP] [CLS] D E F [SEP]" (see indexer logic).
        mask: `torch.BoolTensor`
            Shape: `[batch_size, num_segment_concat_wordpieces]`.
            The mask for the concatenated segments of wordpieces. The same as `segment_concat_mask`
            in `forward()`.
        type_ids: `Optional[torch.LongTensor]`
            Shape: [batch_size, num_segment_concat_wordpieces].

        # Returns:

        token_ids: `torch.LongTensor`
            Shape: [batch_size * num_segments, self._max_length].
        mask: `torch.BoolTensor`
            Shape: [batch_size * num_segments, self._max_length].
        """
        num_segment_concat_wordpieces = token_ids.shape[1]
        num_segments = math.ceil(num_segment_concat_wordpieces / self._max_length)  # type: ignore
        padded_length = num_segments * self._max_length  # type: ignore
        length_to_pad = padded_length - num_segment_concat_wordpieces

        return self.fold(token_ids, length_to_pad), self.fold(mask, length_to_pad)

    def _unfold_long_sequences(
        self,
        embeddings: torch.Tensor,
        mask: torch.Tensor,
        batch_size: int,
        num_segment_concat_wordpieces: int,
    ) -> torch.Tensor:
        """
        We take 2D segments of a long sequence and flatten them out to get the whole sequence
        representation while remove unnecessary special tokens.

        [ [ [CLS]_emb A_emb B_emb C_emb [SEP]_emb ], [ [CLS]_emb D_emb E_emb [SEP]_emb [PAD]_emb ] ]
        -> [ [CLS]_emb A_emb B_emb C_emb D_emb E_emb [SEP]_emb ]

        We truncate the start and end tokens for all segments, recombine the segments,
        and manually add back the start and end tokens.

        # Parameters

        embeddings: `torch.FloatTensor`
            Shape: [batch_size * num_segments, self._max_length, embedding_size].
        mask: `torch.BoolTensor`
            Shape: [batch_size * num_segments, self._max_length].
            The mask for the concatenated segments of wordpieces. The same as `segment_concat_mask`
            in `forward()`.
        batch_size: `int`
        num_segment_concat_wordpieces: `int`
            The length of the original "[ [CLS] A B C [SEP] [CLS] D E F [SEP] ]", i.e.
            the original `token_ids.size(1)`.

        # Returns:

        embeddings: `torch.FloatTensor`
            Shape: [batch_size, self._num_wordpieces, embedding_size].
        """

        device = embeddings.device
        num_segments = int(embeddings.shape[0] / batch_size)
        embedding_size = embeddings.shape[2]

        # We want to remove all segment-level special tokens but maintain sequence-level ones
        num_wordpieces = num_segment_concat_wordpieces - (num_segments - 1) * self._num_added_tokens

        embeddings = embeddings.reshape(batch_size, num_segments * self._max_length, embedding_size)
        mask = mask.reshape(batch_size, num_segments * self._max_length)  # type: ignore
        # Shape: (batch_size,)
        seq_lengths = mask.sum(-1)
        # Shape: (batch_size, self._num_added_end_tokens); this is a broadcast op
        end_token_indices = seq_lengths.unsqueeze(-1) - torch.arange(self._num_added_end_tokens, device=device) - 1

        # Shape: (batch_size, self._num_added_start_tokens, embedding_size)
        start_token_embeddings = embeddings[:, : self._num_added_start_tokens]
        # Shape: (batch_size, self._num_added_end_tokens, embedding_size)
        end_token_embeddings = batched_index_select(embeddings, end_token_indices)

        embeddings = embeddings.reshape(batch_size, num_segments, self._max_length, embedding_size)
        embeddings = embeddings[:, :, self._num_added_start_tokens : embeddings.shape[2] - self._num_added_end_tokens]
        embeddings = embeddings.reshape(batch_size, -1, embedding_size)  # flatten

        # Now try to put end token embeddings back which is a little tricky.

        # The number of segment each sequence spans, excluding padding. Mimicking ceiling operation.
        # Shape: (batch_size,)
        num_effective_segments = (seq_lengths + self._max_length - 1) // self._max_length
        # The number of indices that end tokens should shift back.
        num_removed_non_end_tokens = num_effective_segments * self._num_added_tokens - self._num_added_end_tokens

        # Shape: (batch_size, self._num_added_end_tokens)
        end_token_indices -= num_removed_non_end_tokens.unsqueeze(-1)
        assert (end_token_indices >= self._num_added_start_tokens).all()
        # Add space for end embeddings
        embeddings = torch.cat([embeddings, torch.zeros_like(end_token_embeddings)], 1)
        # Add end token embeddings back
        embeddings.scatter_(1, end_token_indices.unsqueeze(-1).expand_as(end_token_embeddings), end_token_embeddings)

        # Now put back start tokens. We can do this before putting back end tokens, but then
        # we need to change `num_removed_non_end_tokens` a little.
        embeddings = torch.cat([start_token_embeddings, embeddings], 1)

        # Truncate to original length
        return embeddings[:, :num_wordpieces]
