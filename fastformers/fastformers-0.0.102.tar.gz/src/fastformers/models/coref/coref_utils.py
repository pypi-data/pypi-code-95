from typing import Optional, Tuple

import math
import torch

from ...utils import neg_inf


def get_mask_from_sequence_lengths(sequence_lengths: torch.Tensor, max_length: int) -> torch.Tensor:
    """
    Given a variable of shape `(batch_size,)` that represents the sequence lengths of each batch
    element, this function returns a `(batch_size, max_length)` mask variable.  For example, if
    our input was `[2, 2, 3]`, with a `max_length` of 4, we'd return
    `[[1, 1, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0]]`.

    We require `max_length` here instead of just computing it from the input `sequence_lengths`
    because it lets us avoid finding the max, then copying that value from the GPU to the CPU so
    that we can use it to construct a new tensor.
    """
    # (batch_size, max_length)
    range_tensor = torch.ones(
        (sequence_lengths.shape[0], max_length), dtype=torch.long, device=sequence_lengths.device).cumsum(dim=1)
    return sequence_lengths.unsqueeze(1) >= range_tensor


def masked_topk(
        input_: torch.Tensor, mask: torch.Tensor, k: int, dim: int = -1
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Extracts the top-k items along a certain dimension. This is similar to `torch.topk` except:
    (1) we allow of a `mask` that makes the function not consider certain elements;
    (2) the returned top input, mask, and indices are sorted in their original order in the input;
    (3) May use the same k for all dimensions, or different k for each.

    # Parameters

    input_ : `torch.FloatTensor`, required.
        A tensor containing the items that we want to prune.
    mask : `torch.BoolTensor`, required.
        A tensor with the same shape as `input_` that makes the function not consider masked out
        (i.e. False) elements.
    k : `Union[int, torch.LongTensor]`, required.
        If a tensor of shape as `input_` except without dimension `dim`, specifies the number of
        items to keep for each dimension.
        If an int, keep the same number of items for all dimensions.

    # Returns

    top_input : `torch.FloatTensor`
        The values of the top-k scoring items.
        Has the same shape as `input_` except dimension `dim` has value `k` when it's an `int`
        or `k.max()` when it's a tensor.
    top_mask : `torch.BoolTensor`
        The corresponding mask for `top_input`.
        Has the shape as `top_input`.
    top_indices : `torch.IntTensor`
        The indices of the top-k scoring items into the original `input_`
        tensor. This is returned because it can be useful to retain pointers to
        the original items, if each item is being scored by multiple distinct
        scorers, for instance.
        Has the shape as `top_input`.
    """
    dim = (dim + input_.dim()) % input_.dim()

    # We put the dim in question to the last dimension by permutation, and squash all leading dims.

    # [0, 1, ..., dim - 1, dim + 1, ..., input.dim() - 1, dim]
    permutation = list(range(input_.dim()))
    permutation.pop(dim)
    permutation.append(dim)

    # [0, 1, ..., dim - 1, -1, dim, ..., input.dim() - 2]; for restoration
    reverse_permutation = list(range(input_.dim() - 1))
    reverse_permutation.insert(dim, -1)

    permuted_size = list(input_.size())
    permuted_size.pop(dim)
    permuted_size.append(k)

    num_items = input_.shape[dim]
    # (batch_size, num_items)  -- "batch_size" refers to all other dimensions stacked together
    input_ = input_.permute(permutation).reshape(-1, num_items)
    mask = mask.permute(permutation).reshape(-1, num_items)

    # Make sure that we don't select any masked items by setting their scores to be negative.
    input_ = input_.masked_fill(~mask, neg_inf(input_.dtype == torch.half))

    # Shape: (batch_size, max_k)
    _, top_indices = input_.topk(k, 1)

    # Now we order the selected indices in increasing order with
    # respect to their indices (and hence, with respect to the
    # order they originally appeared in the `embeddings` tensor).
    top_indices, _ = top_indices.sort(1)

    # Combine the masks on spans that are out-of-bounds, and the mask on spans that are outside
    # the top k for each sentence.
    # Shape: (batch_size, max_k)
    sequence_mask = mask.gather(1, top_indices)

    # Shape: (batch_size, max_k)
    top_input = input_.gather(1, top_indices)

    return (
        top_input.reshape(permuted_size).permute(reverse_permutation),
        sequence_mask.reshape(permuted_size).permute(reverse_permutation),
        top_indices.reshape(permuted_size).permute(reverse_permutation),
    )


def flatten_and_batch_shift_indices(indices: torch.Tensor, sequence_length: int) -> torch.Tensor:
    """
    This is a subroutine for [`batched_index_select`](./util.md#batched_index_select).
    The given `indices` of size `(batch_size, d_1, ..., d_n)` indexes into dimension 2 of a
    target tensor, which has size `(batch_size, sequence_length, embedding_size)`. This
    function returns a vector that correctly indexes into the flattened target. The sequence
    length of the target must be provided to compute the appropriate offsets.

    ```python
        indices = torch.ones([2,3], dtype=torch.long)
        # Sequence length of the target tensor.
        sequence_length = 10
        shifted_indices = flatten_and_batch_shift_indices(indices, sequence_length)
        # Indices into the second element in the batch are correctly shifted
        # to take into account that the target tensor will be flattened before
        # the indices are applied.
        assert shifted_indices == [1, 1, 1, 11, 11, 11]
    ```

    # Parameters

    indices : `torch.LongTensor`, required.
    sequence_length : `int`, required.
        The length of the sequence the indices index into.
        This must be the second dimension of the tensor.

    # Returns

    offset_indices : `torch.LongTensor`
    """
    # Shape: (batch_size)
    if (indices >= sequence_length).any() or (indices < 0).any():
        raise ValueError
    offsets = torch.arange(indices.shape[0], dtype=torch.long, device=indices.device) * sequence_length
    for _ in range(len(indices.size()) - 1):
        offsets = offsets.unsqueeze(1)

    # Shape: (batch_size, d_1, ..., d_n)
    offset_indices = indices + offsets

    # Shape: (batch_size * d_1 * ... * d_n)
    offset_indices = offset_indices.view(-1)
    return offset_indices


def batched_index_select(
    target: torch.Tensor,
    indices: torch.Tensor,
    flattened_indices: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """
    The given `indices` of size `(batch_size, d_1, ..., d_n)` indexes into the sequence
    dimension (dimension 2) of the target, which has size `(batch_size, sequence_length,
    embedding_size)`.

    This function returns selected values in the target with respect to the provided indices, which
    have size `(batch_size, d_1, ..., d_n, embedding_size)`. This can use the optionally
    precomputed `flattened_indices` with size `(batch_size * d_1 * ... * d_n)` if given.

    An example use case of this function is looking up the start and end indices of spans in a
    sequence tensor. This is used in the
    [CoreferenceResolver](https://docs.allennlp.org/models/main/models/coref/models/coref/)
    model to select contextual word representations corresponding to the start and end indices of
    mentions.

    The key reason this can't be done with basic torch functions is that we want to be able to use look-up
    tensors with an arbitrary number of dimensions (for example, in the coref model, we don't know
    a-priori how many spans we are looking up).

    # Parameters

    target : `torch.Tensor`, required.
        A 3 dimensional tensor of shape (batch_size, sequence_length, embedding_size).
        This is the tensor to be indexed.
    indices : `torch.LongTensor`
        A tensor of shape (batch_size, ...), where each element is an index into the
        `sequence_length` dimension of the `target` tensor.
    flattened_indices : `Optional[torch.Tensor]`, optional (default = `None`)
        An optional tensor representing the result of calling `flatten_and_batch_shift_indices`
        on `indices`. This is helpful in the case that the indices can be flattened once and
        cached for many batch lookups.

    # Returns

    selected_targets : `torch.Tensor`
        A tensor with shape [indices.size(), target.size(-1)] representing the embedded indices
        extracted from the batch flattened target tensor.
    """
    if flattened_indices is None:
        # Shape: (batch_size * d_1 * ... * d_n)
        flattened_indices = flatten_and_batch_shift_indices(indices, target.shape[1])

    # Shape: (batch_size * sequence_length, embedding_size)
    flattened_target = target.view(-1, target.shape[-1])

    # Shape: (batch_size * d_1 * ... * d_n, embedding_size)
    flattened_selected = flattened_target.index_select(0, flattened_indices)
    selected_shape = indices.shape + (target.shape[-1],)
    # Shape: (batch_size, d_1, ..., d_n, embedding_size)
    return flattened_selected.view(selected_shape)


def masked_softmax(vector: torch.Tensor, mask: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """
    `torch.nn.functional.softmax(vector)` does not work if some elements of `vector` should be
    masked.  This performs a softmax on just the non-masked portions of `vector`.  Passing
    `None` in for the mask is also acceptable; you'll just get a regular softmax.

    `vector` can have an arbitrary number of dimensions; the only requirement is that `mask` is
    broadcastable to `vector's` shape.  If `mask` has fewer dimensions than `vector`, we will
    unsqueeze on dimension 1 until they match.  If you need a different unsqueezing of your mask,
    do it yourself before passing the mask into this function.

    If `memory_efficient` is set to true, we will simply use a very large negative number for those
    masked positions so that the probabilities of those positions would be approximately 0.
    This is not accurate in math, but works for most cases and consumes less memory.

    In the case that the input vector is completely masked and `memory_efficient` is false, this function
    returns an array of `0.0`. This behavior may cause `NaN` if this is used as the last layer of
    a model that uses categorical cross-entropy loss. Instead, if `memory_efficient` is true, this function
    will treat every element as equal, and do softmax over equal numbers.
    """
    while mask.dim() < vector.dim():
        mask = mask.unsqueeze(1)
    masked_vector = vector.masked_fill(~mask, neg_inf(vector.dtype == torch.half))
    return masked_vector.softmax(dim=dim)


def weighted_sum(matrix: torch.Tensor, attention: torch.Tensor) -> torch.Tensor:
    """
    Takes a matrix of vectors and a set of weights over the rows in the matrix (which we call an
    "attention" vector), and returns a weighted sum of the rows in the matrix.  This is the typical
    computation performed after an attention mechanism.

    Note that while we call this a "matrix" of vectors and an attention "vector", we also handle
    higher-order tensors.  We always sum over the second-to-last dimension of the "matrix", and we
    assume that all dimensions in the "matrix" prior to the last dimension are matched in the
    "vector".  Non-matched dimensions in the "vector" must be `directly after the batch dimension`.

    For example, say I have a "matrix" with dimensions `(batch_size, num_queries, num_words,
    embedding_dim)`.  The attention "vector" then must have at least those dimensions, and could
    have more. Both:

        - `(batch_size, num_queries, num_words)` (distribution over words for each query)
        - `(batch_size, num_documents, num_queries, num_words)` (distribution over words in a
          query for each document)

    are valid input "vectors", producing tensors of shape:
    `(batch_size, num_queries, embedding_dim)` and
    `(batch_size, num_documents, num_queries, embedding_dim)` respectively.
    """
    # We'll special-case a few settings here, where there are efficient (but poorly-named)
    # operations in pytorch that already do the computation we need.
    if attention.dim() == 2 and matrix.dim() == 3:
        return attention.unsqueeze(1).bmm(matrix).squeeze(1)
    if attention.dim() == 3 and matrix.dim() == 3:
        return attention.bmm(matrix)
    if matrix.dim() - 1 < attention.dim():
        expanded_size = list(matrix.size())
        for i in range(attention.dim() - matrix.dim() + 1):
            matrix = matrix.unsqueeze(1)
            expanded_size.insert(i + 1, attention.shape[i + 1])
        matrix = matrix.expand(expanded_size)
    intermediate = attention.unsqueeze(-1).expand_as(matrix) * matrix
    return intermediate.sum(dim=-2)


def bucket_values(distances: torch.Tensor, num_identity_buckets: int = 4, num_total_buckets: int = 10) -> torch.Tensor:
    """
    Places the given values (designed for distances) into `num_total_buckets`semi-logscale
    buckets, with `num_identity_buckets` of these capturing single values.

    The default settings will bucket values into the following buckets:
    [0, 1, 2, 3, 4, 5-7, 8-15, 16-31, 32-63, 64+].

    # Parameters

    distances : `torch.Tensor`, required.
        A Tensor of any size, to be bucketed.
    num_identity_buckets: `int`, optional (default = `4`).
        The number of identity buckets (those only holding a single value).
    num_total_buckets : `int`, (default = `10`)
        The total number of buckets to bucket values into.

    # Returns

    `torch.Tensor`
        A tensor of the same shape as the input, containing the indices of the buckets
        the values were placed in.
    """
    # Chunk the values into semi-logscale buckets using .floor().
    # This is a semi-logscale bucketing because we divide by log(2) after taking the log.
    # We do this to make the buckets more granular in the initial range, where we expect
    # most values to fall. We then add (num_identity_buckets - 1) because we want these indices
    # to start _after_ the fixed number of buckets which we specified would only hold single values.
    logspace_index = (distances.float().log() / math.log(2)).floor().long() + (
        num_identity_buckets - 1
    )
    # create a mask for values which will go into single number buckets (i.e not a range).
    use_identity_mask = (distances <= num_identity_buckets).long()
    use_buckets_mask = 1 + (-1 * use_identity_mask)
    # Use the original values if they are less than num_identity_buckets, otherwise
    # use the logspace indices.
    combined_index = use_identity_mask * distances + use_buckets_mask * logspace_index
    # Clamp to put anything > num_total_buckets into the final bucket.
    return combined_index.clamp(0, num_total_buckets - 1)


def batched_span_select(target: torch.Tensor, spans: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    The given `spans` of size `(batch_size, num_spans, 2)` indexes into the sequence
    dimension (dimension 2) of the target, which has size `(batch_size, sequence_length,
    embedding_size)`.

    This function returns segmented spans in the target with respect to the provided span indices.

    # Parameters

    target : `torch.Tensor`, required.
        A 3 dimensional tensor of shape (batch_size, sequence_length, embedding_size).
        This is the tensor to be indexed.
    indices : `torch.LongTensor`
        A 3 dimensional tensor of shape (batch_size, num_spans, 2) representing start and end
        indices (both inclusive) into the `sequence_length` dimension of the `target` tensor.

    # Returns

    span_embeddings : `torch.Tensor`
        A tensor with shape (batch_size, num_spans, max_batch_span_width, embedding_size]
        representing the embedded spans extracted from the batch flattened target tensor.
    span_mask: `torch.BoolTensor`
        A tensor with shape (batch_size, num_spans, max_batch_span_width) representing the mask on
        the returned span embeddings.
    """
    # both of shape (batch_size, num_spans, 1)
    span_starts, span_ends = spans.split(1, dim=-1)

    # shape (batch_size, num_spans, 1)
    # These span widths are off by 1, because the span ends are `inclusive`.
    span_widths = span_ends - span_starts

    # We need to know the maximum span width so we can
    # generate indices to extract the spans from the sequence tensor.
    # These indices will then get masked below, such that if the length
    # of a given span is smaller than the max, the rest of the values
    # are masked.
    max_batch_span_width = span_widths.max() + 1

    # Shape: (1, 1, max_batch_span_width)
    max_span_range_indices = torch.arange(max_batch_span_width, dtype=torch.long, device=span_widths.device).view(
        1, 1, -1)
    # Shape: (batch_size, num_spans, max_batch_span_width)
    # This is a broadcasted comparison - for each span we are considering,
    # we are creating a range vector of size max_span_width, but masking values
    # which are greater than the actual length of the span.
    #
    # We're using <= here (and for the mask below) because the span ends are
    # inclusive, so we want to include indices which are equal to span_widths rather
    # than using it as a non-inclusive upper bound.
    span_mask = max_span_range_indices <= span_widths
    raw_span_indices = span_starts + max_span_range_indices
    # We also don't want to include span indices which greater than the sequence_length,
    # which happens because some spans near the end of the sequence
    # have a start index + max_batch_span_width > sequence_length, so we add this to the mask here.
    span_mask = span_mask & (raw_span_indices < target.shape[1]) & (0 <= raw_span_indices)
    span_indices = raw_span_indices * span_mask

    # Shape: (batch_size, num_spans, max_batch_span_width, embedding_dim)
    span_embeddings = batched_index_select(target, span_indices)

    return span_embeddings, span_mask
