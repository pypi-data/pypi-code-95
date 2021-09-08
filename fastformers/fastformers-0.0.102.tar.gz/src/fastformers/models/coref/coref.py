from typing import Tuple

import os
import math

import torch
from torch.nn.functional import relu

from allennlp.data import Vocabulary
from allennlp.models.model import Model
from allennlp.modules import FeedForward, GatedSum
from allennlp.modules import Seq2SeqEncoder, TimeDistributed, TextFieldEmbedder
from allennlp.modules.span_extractors import SelfAttentiveSpanExtractor, EndpointSpanExtractor
from allennlp.common import Params

from .coref_utils import (
    masked_topk, flatten_and_batch_shift_indices, batched_index_select, masked_softmax,
    weighted_sum, bucket_values)
from ...utils import neg_inf


class CoreferencePredictor(Model):
    def __init__(
            self,
            vocab: Vocabulary,
            text_field_embedder: TextFieldEmbedder,
            context_layer: Seq2SeqEncoder,
            mention_feedforward: FeedForward,
            antecedent_feedforward: FeedForward,
            feature_size: int,
            max_span_width: int,
            spans_per_word: float,
            max_antecedents: int,
            coarse_to_fine: bool = False,
            inference_order: int = 1,
            lexical_dropout: float = 0.2,
            **kwargs
    ) -> None:
        super().__init__(vocab, **kwargs)

        self._text_field_embedder = text_field_embedder
        self._context_layer = context_layer
        self._mention_feedforward = TimeDistributed(mention_feedforward)
        self._mention_scorer = TimeDistributed(
            torch.nn.Linear(mention_feedforward.get_output_dim(), 1)
        )
        self._antecedent_feedforward = TimeDistributed(antecedent_feedforward)
        self._antecedent_scorer = TimeDistributed(
            torch.nn.Linear(antecedent_feedforward.get_output_dim(), 1)
        )

        self._endpoint_span_extractor = EndpointSpanExtractor(
            context_layer.get_output_dim(),
            combination="x,y",
            num_width_embeddings=max_span_width,
            span_width_embedding_dim=feature_size,
            bucket_widths=False,
        )
        self._attentive_span_extractor = SelfAttentiveSpanExtractor(input_dim=text_field_embedder.get_output_dim())

        # 10 possible distance buckets.
        self._num_distance_buckets = 10
        self._distance_embedding = torch.nn.Embedding(
            embedding_dim=feature_size, num_embeddings=self._num_distance_buckets)

        self._spans_per_word = spans_per_word
        self._max_antecedents = max_antecedents

        self._coarse2fine_scorer = torch.nn.Linear(
            mention_feedforward.get_input_dim(), mention_feedforward.get_input_dim())
        self._inference_order = inference_order
        self._span_updating_gated_sum = GatedSum(mention_feedforward.get_input_dim())

        self.pad_map = {'spans': -1}

    @classmethod
    def from_pretrained(cls, model_path: str):
        model_params = Params.from_file(os.path.join(model_path, 'config.json'))['model']
        for key in ('type', 'initializer'):
            del model_params[key]
        model = cls.from_params(vocab=None, params=model_params, serialization_dir=model_path)
        model.load_state_dict(torch.load(os.path.join(model_path, 'weights.th'), map_location='cpu'), strict=True)
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model

    def forward(self, spans, token_ids, mask, offsets, segment_concat_mask):
        text = {'tokens': {
            'token_ids': token_ids, 'mask': mask, 'type_ids': None, 'offsets': offsets,
            'wordpiece_mask': None, 'segment_concat_mask': segment_concat_mask
        }}

        # Shape: (batch_size, document_length, embedding_size)
        text_embeddings = self._text_field_embedder(text)

        batch_size, num_spans = spans.shape[:2]
        document_length = text_embeddings.shape[1]

        # Shape: (batch_size, num_spans)
        span_mask = (spans[:, :, 0] >= 0).squeeze(-1)
        # SpanFields return -1 when they are used as padding. As we do
        # some comparisons based on span widths when we attend over the
        # span representations that we generate from these indices, we
        # need them to be <= 0. This is only relevant in edge cases where
        # the number of spans we consider after the pruning stage is >= the
        # total number of spans, because in this case, it is possible we might
        # consider a masked span.
        # Shape: (batch_size, num_spans, 2)
        spans = relu(spans.float()).long()

        # Shape: (batch_size, document_length, encoding_dim)
        contextualized_embeddings = text_embeddings * mask.unsqueeze(dim=-1)
        # Shape: (batch_size, num_spans, 2 * encoding_dim + feature_size)
        endpoint_span_embeddings = self._endpoint_span_extractor(contextualized_embeddings, spans)
        # Shape: (batch_size, num_spans, emebedding_size)
        attended_span_embeddings = self._attentive_span_extractor(text_embeddings, spans)

        # Shape: (batch_size, num_spans, emebedding_size + 2 * encoding_dim + feature_size)
        span_embeddings = torch.cat([endpoint_span_embeddings, attended_span_embeddings], -1)

        # Prune based on mention scores.
        num_spans_to_keep = min(int(math.floor(self._spans_per_word * document_length)), num_spans)

        # Shape: (batch_size, num_spans)
        span_mention_scores = self._mention_scorer(self._mention_feedforward(span_embeddings)).squeeze(-1)
        # Shape: (batch_size, num_spans) for all 3 tensors
        top_span_mention_scores, top_span_mask, top_span_indices = masked_topk(
            span_mention_scores, span_mask, num_spans_to_keep)

        # Shape: (batch_size * num_spans_to_keep)
        # torch.index_select only accepts 1D indices, but here
        # we need to select spans for each element in the batch.
        # This reformats the indices to take into account their
        # index into the batch. We precompute this here to make
        # the multiple calls to util.batched_index_select below more efficient.
        flat_top_span_indices = flatten_and_batch_shift_indices(top_span_indices, num_spans)

        # Compute final predictions for which spans to consider as mentions.
        # Shape: (batch_size, num_spans_to_keep, 2)
        top_spans = batched_index_select(spans, top_span_indices, flat_top_span_indices)
        # Shape: (batch_size, num_spans_to_keep, embedding_size)
        top_span_embeddings = batched_index_select(span_embeddings, top_span_indices, flat_top_span_indices)

        # Compute indices for antecedent spans to consider.
        max_antecedents = min(self._max_antecedents, num_spans_to_keep)

        # Now that we have our variables in terms of num_spans_to_keep, we need to
        # compare span pairs to decide each span's antecedent. Each span can only
        # have prior spans as antecedents, and we only consider up to max_antecedents
        # prior spans. So the first thing we do is construct a matrix mapping a span's
        # index to the indices of its allowed antecedents.

        # Once we have this matrix, we reformat our variables again to get embeddings
        # for all valid antecedents for each span. This gives us variables with shapes
        # like (batch_size, num_spans_to_keep, max_antecedents, embedding_size), which
        # we can use to make coreference decisions between valid span pairs.

        # Shape: (batch_size, num_spans_to_keep, max_antecedents) for all 4 tensors
        top_partial_coreference_scores, top_antecedent_mask, top_antecedent_offsets, top_antecedent_indices = self.\
            _coarse_to_fine_pruning(top_span_embeddings, top_span_mention_scores, top_span_mask, max_antecedents)

        flat_top_antecedent_indices = flatten_and_batch_shift_indices(top_antecedent_indices, num_spans_to_keep)

        # Shape: (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        top_antecedent_embeddings = batched_index_select(
            top_span_embeddings, top_antecedent_indices, flat_top_antecedent_indices)
        # Shape: (batch_size, num_spans_to_keep, 1 + max_antecedents)
        coreference_scores = self._compute_coreference_scores(
            top_span_embeddings,
            top_antecedent_embeddings,
            top_partial_coreference_scores,
            top_antecedent_mask,
            top_antecedent_offsets,
        )

        dummy_mask = torch.ones(
            (batch_size, num_spans_to_keep, 1), dtype=torch.bool, device=top_antecedent_mask.device)
        # Shape: (batch_size, num_spans_to_keep, 1 + max_antecedents,)
        top_antecedent_with_dummy_mask = torch.cat([dummy_mask, top_antecedent_mask], -1)
        # Shape: (batch_size, num_spans_to_keep, 1 + max_antecedents)
        attention_weight = masked_softmax(
            coreference_scores, top_antecedent_with_dummy_mask
        )
        # Shape: (batch_size, num_spans_to_keep, 1 + max_antecedents, embedding_size)
        top_antecedent_with_dummy_embeddings = torch.cat(
            [top_span_embeddings.unsqueeze(2), top_antecedent_embeddings], 2
        )
        # Shape: (batch_size, num_spans_to_keep, embedding_size)
        attended_embeddings = weighted_sum(top_antecedent_with_dummy_embeddings, attention_weight)
        # Shape: (batch_size, num_spans_to_keep, embedding_size)
        top_span_embeddings = self._span_updating_gated_sum(top_span_embeddings, attended_embeddings)

        # Shape: (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        top_antecedent_embeddings = batched_index_select(
            top_span_embeddings, top_antecedent_indices, flat_top_antecedent_indices
        )
        # Shape: (batch_size, num_spans_to_keep, 1 + max_antecedents)
        coreference_scores = self._compute_coreference_scores(
            top_span_embeddings,
            top_antecedent_embeddings,
            top_partial_coreference_scores,
            top_antecedent_mask,
            top_antecedent_offsets
        )

        # We now have, for each span which survived the pruning stage,
        # a predicted antecedent. This implies a clustering if we group
        # mentions which refer to each other in a chain.
        # Shape: (batch_size, num_spans_to_keep)
        _, predicted_antecedents = coreference_scores.max(2)
        # Subtract one here because index 0 is the "no antecedent" class,
        # so this makes the indices line up with actual spans if the prediction
        # is greater than -1.
        predicted_antecedents -= 1

        return {
            'top_spans': top_spans.detach().cpu(),
            'antecedent_indices': top_antecedent_indices.detach().cpu(),
            'predicted_antecedents': predicted_antecedents.detach().cpu()
        }

    def _coarse_to_fine_pruning(
        self,
        top_span_embeddings: torch.Tensor,
        top_span_mention_scores: torch.Tensor,
        top_span_mask: torch.Tensor,
        max_antecedents: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Generates antecedents for each span and prunes down to `max_antecedents`. This method
        prunes antecedents using a fast bilinar interaction score between a span and a candidate
        antecedent, and the highest-scoring antecedents are kept.

        # Parameters

        top_span_embeddings: `torch.FloatTensor`, required.
            The embeddings of the top spans.
            (batch_size, num_spans_to_keep, embedding_size).
        top_span_mention_scores: `torch.FloatTensor`, required.
            The mention scores of the top spans.
            (batch_size, num_spans_to_keep).
        top_span_mask: `torch.BoolTensor`, required.
            The mask for the top spans.
            (batch_size, num_spans_to_keep).
        max_antecedents: `int`, required.
            The maximum number of antecedents to keep for each span.

        # Returns

        top_partial_coreference_scores: `torch.FloatTensor`
            The partial antecedent scores for each span-antecedent pair. Computed by summing
            the span mentions scores of the span and the antecedent as well as a bilinear
            interaction term. This score is partial because compared to the full coreference scores,
            it lacks the interaction term
            `w * FFNN([g_i, g_j, g_i * g_j, features])`.
            `(batch_size, num_spans_to_keep, max_antecedents)`
        top_antecedent_mask: `torch.BoolTensor`
            The mask representing whether each antecedent span is valid. Required since
            different spans have different numbers of valid antecedents. For example, the first
            span in the document should have no valid antecedents.
            `(batch_size, num_spans_to_keep, max_antecedents)`
        top_antecedent_offsets: `torch.LongTensor`
            The distance between the span and each of its antecedents in terms of the number
            of considered spans (i.e not the word distance between the spans).
            `(batch_size, num_spans_to_keep, max_antecedents)`
        top_antecedent_indices: `torch.LongTensor`
            The indices of every antecedent to consider with respect to the top k spans.
            `(batch_size, num_spans_to_keep, max_antecedents)`
        """
        batch_size, num_spans_to_keep = top_span_embeddings.size()[:2]

        # Shape: (1, num_spans_to_keep, num_spans_to_keep)
        _, _, valid_antecedent_mask = self._generate_valid_antecedents(
            num_spans_to_keep, num_spans_to_keep, top_span_embeddings.device
        )

        mention_one_score = top_span_mention_scores.unsqueeze(1)
        mention_two_score = top_span_mention_scores.unsqueeze(2)
        bilinear_weights = self._coarse2fine_scorer(top_span_embeddings).transpose(1, 2)
        bilinear_score = torch.matmul(top_span_embeddings, bilinear_weights)
        # Shape: (batch_size, num_spans_to_keep, num_spans_to_keep); broadcast op
        partial_antecedent_scores = mention_one_score + mention_two_score + bilinear_score

        # Shape: (batch_size, num_spans_to_keep, num_spans_to_keep); broadcast op
        span_pair_mask = top_span_mask.unsqueeze(-1) & valid_antecedent_mask

        # Shape: (batch_size, num_spans_to_keep, max_antecedents) * 3
        top_partial_coreference_scores, top_antecedent_mask, top_antecedent_indices = masked_topk(
            partial_antecedent_scores, span_pair_mask, max_antecedents)

        top_span_range = torch.arange(num_spans_to_keep, dtype=torch.long, device=top_antecedent_mask.device)
        # Shape: (num_spans_to_keep, num_spans_to_keep); broadcast op
        valid_antecedent_offsets = top_span_range.unsqueeze(-1) - top_span_range.unsqueeze(0)

        top_antecedent_offsets = batched_index_select(
            valid_antecedent_offsets.unsqueeze(0)
            .expand(batch_size, num_spans_to_keep, num_spans_to_keep)
            .reshape(batch_size * num_spans_to_keep, num_spans_to_keep, 1),
            top_antecedent_indices.view(-1, max_antecedents),
        ).reshape(batch_size, num_spans_to_keep, max_antecedents)

        return top_partial_coreference_scores, top_antecedent_mask, top_antecedent_offsets, top_antecedent_indices

    def _compute_span_pair_embeddings(
            self, top_span_embeddings: torch.Tensor, antecedent_embeddings: torch.Tensor,
            antecedent_offsets: torch.Tensor) -> torch.Tensor:
        """
        Computes an embedding representation of pairs of spans for the pairwise scoring function
        to consider. This includes both the original span representations, the element-wise
        similarity of the span representations, and an embedding representation of the distance
        between the two spans.

        # Parameters

        top_span_embeddings : `torch.FloatTensor`, required.
            Embedding representations of the top spans. Has shape
            (batch_size, num_spans_to_keep, embedding_size).
        antecedent_embeddings : `torch.FloatTensor`, required.
            Embedding representations of the antecedent spans we are considering
            for each top span. Has shape
            (batch_size, num_spans_to_keep, max_antecedents, embedding_size).
        antecedent_offsets : `torch.IntTensor`, required.
            The offsets between each top span and its antecedent spans in terms
            of spans we are considering. Has shape (batch_size, num_spans_to_keep, max_antecedents).

        # Returns

        span_pair_embeddings : `torch.FloatTensor`
            Embedding representation of the pair of spans to consider. Has shape
            (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        """
        # Shape: (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        target_embeddings = top_span_embeddings.unsqueeze(2).expand_as(antecedent_embeddings)

        # Shape: (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        antecedent_distance_embeddings = self._distance_embedding(
            bucket_values(antecedent_offsets, num_total_buckets=self._num_distance_buckets))

        # Shape: (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        return torch.cat(
            [
                target_embeddings,
                antecedent_embeddings,
                antecedent_embeddings * target_embeddings,
                antecedent_distance_embeddings,
            ], -1)

    def _compute_coreference_scores(
        self,
        top_span_embeddings: torch.Tensor,
        top_antecedent_embeddings: torch.Tensor,
        top_partial_coreference_scores: torch.Tensor,
        top_antecedent_mask: torch.Tensor,
        top_antecedent_offsets: torch.Tensor,
    ) -> torch.Tensor:
        """
        Computes scores for every pair of spans. Additionally, a dummy label is included,
        representing the decision that the span is not coreferent with anything. For the dummy
        label, the score is always zero. For the true antecedent spans, the score consists of
        the pairwise antecedent score and the unary mention scores for the span and its
        antecedent. The factoring allows the model to blame many of the absent links on bad
        spans, enabling the pruning strategy used in the forward pass.

        # Parameters

        top_span_embeddings : `torch.FloatTensor`, required.
            Embedding representations of the kept spans. Has shape
            (batch_size, num_spans_to_keep, embedding_size)
        top_antecedent_embeddings: `torch.FloatTensor`, required.
            The embeddings of antecedents for each span candidate. Has shape
            (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        top_partial_coreference_scores : `torch.FloatTensor`, required.
            Sum of span mention score and antecedent mention score. The coarse to fine settings
            has an additional term which is the coarse bilinear score.
            (batch_size, num_spans_to_keep, max_antecedents).
        top_antecedent_mask : `torch.BoolTensor`, required.
            The mask for valid antecedents.
            (batch_size, num_spans_to_keep, max_antecedents).
        top_antecedent_offsets : `torch.FloatTensor`, required.
            The distance between the span and each of its antecedents in terms of the number
            of considered spans (i.e not the word distance between the spans).
            (batch_size, num_spans_to_keep, max_antecedents).

        # Returns

        coreference_scores : `torch.FloatTensor`
            A tensor of shape (batch_size, num_spans_to_keep, max_antecedents + 1),
            representing the unormalised score for each (span, antecedent) pair
            we considered.

        """
        # Shape: (batch_size, num_spans_to_keep, max_antecedents, embedding_size)
        span_pair_embeddings = self._compute_span_pair_embeddings(
            top_span_embeddings, top_antecedent_embeddings, top_antecedent_offsets
        )

        # Shape: (batch_size, num_spans_to_keep, max_antecedents)
        antecedent_scores = self._antecedent_scorer(self._antecedent_feedforward(span_pair_embeddings)).squeeze(-1)
        antecedent_scores += top_partial_coreference_scores
        antecedent_scores = antecedent_scores.masked_fill(
            ~top_antecedent_mask, neg_inf(antecedent_scores.dtype == torch.half))

        # Shape: (batch_size, num_spans_to_keep, 1)
        dummy_scores = antecedent_scores.new_zeros(antecedent_scores.shape[:2] + (1,))

        # Shape: (batch_size, num_spans_to_keep, max_antecedents + 1)
        return torch.cat([dummy_scores, antecedent_scores], -1)

    @staticmethod
    def _generate_valid_antecedents(
            num_spans_to_keep: int, max_antecedents: int, device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        This method generates possible antecedents per span which survived the pruning
        stage. This procedure is `generic across the batch`. The reason this is the case is
        that each span in a batch can be coreferent with any previous span, but here we
        are computing the possible `indices` of these spans. So, regardless of the batch,
        the 1st span _cannot_ have any antecedents, because there are none to select from.
        Similarly, each element can only predict previous spans, so this returns a matrix
        of shape (num_spans_to_keep, max_antecedents), where the (i,j)-th index is equal to
        (i - 1) - j if j <= i, or zero otherwise.

        # Parameters

        num_spans_to_keep : `int`, required.
            The number of spans that were kept while pruning.
        max_antecedents : `int`, required.
            The maximum number of antecedent spans to consider for every span.
        device : `int`, required.
            The CUDA device to use.

        # Returns

        valid_antecedent_indices : `torch.LongTensor`
            The indices of every antecedent to consider with respect to the top k spans.
            Has shape `(num_spans_to_keep, max_antecedents)`.
        valid_antecedent_offsets : `torch.LongTensor`
            The distance between the span and each of its antecedents in terms of the number
            of considered spans (i.e not the word distance between the spans).
            Has shape `(1, max_antecedents)`.
        valid_antecedent_mask : `torch.BoolTensor`
            The mask representing whether each antecedent span is valid. Required since
            different spans have different numbers of valid antecedents. For example, the first
            span in the document should have no valid antecedents.
            Has shape `(1, num_spans_to_keep, max_antecedents)`.
        """
        # Shape: (num_spans_to_keep, 1)
        target_indices = torch.arange(num_spans_to_keep, dtype=torch.long, device=device).unsqueeze(1)

        # Shape: (1, max_antecedents)
        valid_antecedent_offsets = (torch.arange(max_antecedents, dtype=torch.long, device=device) + 1).unsqueeze(0)

        # This is a broadcasted subtraction.
        # Shape: (num_spans_to_keep, max_antecedents)
        raw_antecedent_indices = target_indices - valid_antecedent_offsets

        # In our matrix of indices, the upper triangular part will be negative
        # because the offsets will be > the target indices. We want to mask these,
        # because these are exactly the indices which we don't want to predict, per span.
        # Shape: (1, num_spans_to_keep, max_antecedents)
        valid_antecedent_mask = (raw_antecedent_indices >= 0).unsqueeze(0)

        # Shape: (num_spans_to_keep, max_antecedents)
        valid_antecedent_indices = raw_antecedent_indices.clamp(min=0)
        return valid_antecedent_indices, valid_antecedent_offsets, valid_antecedent_mask
