from typing import Any, Tuple, Dict

import copy
import os
import json
import math

import torch
from torch import nn
from torch.nn.functional import relu, softmax

from transformers.modeling_outputs import BaseModelOutput, BaseModelOutputWithPastAndCrossAttentions, Seq2SeqLMOutput
from transformers.generation_utils import GenerationMixin


class Linear(torch.nn.Linear):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        torch.nn.Module.__init__(self)
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)


class T5LayerNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        """
        Construct a layernorm module in the T5 style No bias and no subtraction of mean.
        """
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states):
        # layer norm should always be calculated in float32
        variance = hidden_states.to(torch.float32).pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(self.weight.dtype)


class T5DenseReluDense(nn.Module):
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.wi = Linear(d_model, d_ff, bias=False)
        self.wo = Linear(d_ff, d_model, bias=False)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.wi(hidden_states)
        hidden_states = relu(hidden_states)
        return self.wo(hidden_states)


class T5LayerFF(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.DenseReluDense = T5DenseReluDense(d_model=config['d_model'], d_ff=config['d_ff'])
        self.layer_norm = T5LayerNorm(config['d_model'], eps=config['layer_norm_epsilon'])

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        forwarded_states = self.layer_norm(hidden_states)
        forwarded_states = self.DenseReluDense(forwarded_states)
        return hidden_states + forwarded_states


class T5Attention(nn.Module):
    def __init__(self, config: dict, has_relative_attention_bias=False):
        super().__init__()
        self.is_decoder = config['is_decoder']
        self.has_relative_attention_bias = has_relative_attention_bias

        self.relative_attention_num_buckets = config['relative_attention_num_buckets']
        self.d_model = config['d_model']
        self.key_value_proj_dim = config['d_kv']
        self.n_heads = config['num_heads']
        self.inner_dim = self.n_heads * self.key_value_proj_dim

        # Mesh TensorFlow initialization to avoid scaling before softmax
        self.q = Linear(self.d_model, self.inner_dim, bias=False)
        self.k = Linear(self.d_model, self.inner_dim, bias=False)
        self.v = Linear(self.d_model, self.inner_dim, bias=False)
        self.o = Linear(self.inner_dim, self.d_model, bias=False)

        if self.has_relative_attention_bias:
            self.relative_attention_bias = nn.Embedding(self.relative_attention_num_buckets, self.n_heads)

    @staticmethod
    def _relative_position_bucket(
            relative_position, bidirectional=True, num_buckets=32, max_distance=128) -> torch.Tensor:
        if bidirectional:
            num_buckets //= 2
            relative_buckets = (relative_position > 0).to(torch.long) * num_buckets
            relative_position = torch.abs(relative_position)
        else:
            relative_buckets = 0
            relative_position = -torch.min(relative_position, torch.zeros_like(relative_position))
        # now relative_position is in the range [0, inf)

        # half of the buckets are for exact increments in positions
        max_exact = num_buckets // 2
        is_small = relative_position < max_exact

        # The other half of the buckets are for logarithmically bigger bins in positions up to max_distance
        relative_postion_if_large = max_exact + (
            torch.log(relative_position.float() / max_exact)
            / math.log(max_distance / max_exact)
            * (num_buckets - max_exact)
        ).to(torch.long)
        relative_postion_if_large = torch.min(
            relative_postion_if_large, torch.full_like(relative_postion_if_large, num_buckets - 1)
        )

        return torch.where(is_small, relative_position, relative_postion_if_large) + relative_buckets

    def compute_bias(self, query_length: int, key_length: int) -> torch.Tensor:
        """ Compute binned relative position bias """
        context_position = torch.arange(query_length, dtype=torch.long).unsqueeze(1)
        memory_position = torch.arange(key_length, dtype=torch.long).unsqueeze(0)
        relative_position = memory_position - context_position  # shape (query_length, key_length)
        relative_position_bucket = self._relative_position_bucket(
            relative_position,  # shape (query_length, key_length)
            bidirectional=(not self.is_decoder),
            num_buckets=self.relative_attention_num_buckets,
        )
        relative_position_bucket = relative_position_bucket.to(self.relative_attention_bias.weight.device)
        values = self.relative_attention_bias(relative_position_bucket)  # shape (query_length, key_length, num_heads)
        return values.permute([2, 0, 1]).unsqueeze(0)  # shape (1, num_heads, query_length, key_length)

    def forward(
        self,
        hidden_states,
        mask=None,
        key_value_states=None,
        position_bias=None,
        past_key_value=None,
        layer_head_mask=None,
        query_length=None,
        use_cache=False
    ):
        """
        Self-attention (if key_value_states is None) or attention over source sentence (provided by key_value_states).
        """
        # Input is (batch_size, seq_length, dim)
        # Mask is (batch_size, key_length) (non-causal) or (batch_size, key_length, key_length)
        # past_key_value[0] is (batch_size, n_heads, q_len - 1, dim_per_head)
        batch_size, seq_length = hidden_states.shape[:2]

        real_seq_length = seq_length

        if past_key_value is not None:
            real_seq_length += past_key_value[0].shape[2] if query_length is None else query_length

        key_length = real_seq_length if key_value_states is None else key_value_states.shape[1]

        def shape(states):
            """  projection """
            return states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)

        def unshape(states):
            """  reshape """
            return states.transpose(1, 2).contiguous().view(batch_size, -1, self.inner_dim)

        def project(hidden_states, proj_layer, key_value_states, past_key_value):
            """ projects hidden states correctly to key/query states """
            if key_value_states is None:
                # self-attn
                # (batch_size, n_heads, seq_length, dim_per_head)
                hidden_states = shape(proj_layer(hidden_states))
            elif past_key_value is None:
                # cross-attn
                # (batch_size, n_heads, seq_length, dim_per_head)
                hidden_states = shape(proj_layer(key_value_states))

            if past_key_value is not None:
                if key_value_states is None:
                    # self-attn
                    # (batch_size, n_heads, key_length, dim_per_head)
                    hidden_states = torch.cat([past_key_value, hidden_states], dim=2)
                else:
                    # cross-attn
                    hidden_states = past_key_value
            return hidden_states

        # get query states
        query_states = shape(self.q(hidden_states))  # (batch_size, n_heads, seq_length, dim_per_head)

        # get key/value states
        key_states = project(
            hidden_states, self.k, key_value_states, past_key_value[0] if past_key_value is not None else None
        )
        value_states = project(
            hidden_states, self.v, key_value_states, past_key_value[1] if past_key_value is not None else None
        )

        # compute scores
        scores = torch.matmul(query_states, key_states.transpose(3, 2))

        if position_bias is None:
            position_bias = (
                self.compute_bias(real_seq_length, key_length) if self.has_relative_attention_bias else
                torch.zeros((1, self.n_heads, real_seq_length, key_length), device=scores.device, dtype=scores.dtype)
            )

            # if key and values are already calculated
            # we want only the last query position bias
            if past_key_value is not None:
                position_bias = position_bias[:, :, -seq_length:, :]

            if mask is not None:
                position_bias = position_bias + mask  # (batch_size, n_heads, seq_length, key_length)

        scores += position_bias
        attn_weights = softmax(scores.float(), dim=-1).type_as(scores)  # (batch_size, n_heads, seq_length, key_length)

        # Mask heads if we want to
        if layer_head_mask is not None:
            attn_weights = attn_weights * layer_head_mask

        attn_output = unshape(torch.matmul(attn_weights, value_states))  # (batch_size, seq_length, dim)
        attn_output = self.o(attn_output)

        present_key_value_state = (key_states, value_states) if (self.is_decoder and use_cache) else None
        return attn_output, present_key_value_state, position_bias


class T5LayerSelfAttention(nn.Module):
    def __init__(self, config: dict, has_relative_attention_bias=False):
        super().__init__()
        self.SelfAttention = T5Attention(config, has_relative_attention_bias=has_relative_attention_bias)
        self.layer_norm = T5LayerNorm(config['d_model'], eps=config['layer_norm_epsilon'])

    def forward(
        self,
        hidden_states,
        attention_mask=None,
        position_bias=None,
        layer_head_mask=None,
        past_key_value=None,
        use_cache=False
    ):
        normed_hidden_states = self.layer_norm(hidden_states)
        attention_output = self.SelfAttention(
            normed_hidden_states,
            mask=attention_mask,
            position_bias=position_bias,
            layer_head_mask=layer_head_mask,
            past_key_value=past_key_value,
            use_cache=use_cache
        )
        return (hidden_states + attention_output[0],) + attention_output[1:]  # add attentions if we output them


class T5LayerCrossAttention(nn.Module):
    def __init__(self, config: dict):
        super().__init__()
        self.EncDecAttention = T5Attention(config, has_relative_attention_bias=False)
        self.layer_norm = T5LayerNorm(config['d_model'], eps=config['layer_norm_epsilon'])

    def forward(
        self,
        hidden_states,
        key_value_states,
        attention_mask=None,
        position_bias=None,
        layer_head_mask=None,
        past_key_value=None,
        use_cache=False,
        query_length=None
    ):
        normed_hidden_states = self.layer_norm(hidden_states)
        attention_output = self.EncDecAttention(
            normed_hidden_states,
            mask=attention_mask,
            key_value_states=key_value_states,
            position_bias=position_bias,
            layer_head_mask=layer_head_mask,
            past_key_value=past_key_value,
            use_cache=use_cache,
            query_length=query_length
        )
        return (hidden_states + attention_output[0],) + attention_output[1:]


class T5Block(nn.Module):
    def __init__(self, config: dict, has_relative_attention_bias=False):
        super().__init__()
        self.is_decoder = config['is_decoder']
        self.layer = nn.ModuleList()
        self.layer.append(T5LayerSelfAttention(config, has_relative_attention_bias=has_relative_attention_bias))
        if self.is_decoder:
            self.layer.append(T5LayerCrossAttention(config))

        self.layer.append(T5LayerFF(config))

    def forward(
        self,
        hidden_states,
        attention_mask=None,
        position_bias=None,
        encoder_hidden_states=None,
        encoder_attention_mask=None,
        encoder_decoder_position_bias=None,
        layer_head_mask=None,
        encoder_layer_head_mask=None,
        past_key_value=None,
        use_cache=False
    ):

        if past_key_value is not None:
            self_attn_past_key_value = past_key_value[:2]
            cross_attn_past_key_value = past_key_value[2:]
        else:
            self_attn_past_key_value, cross_attn_past_key_value = None, None

        self_attention_outputs = self.layer[0](
            hidden_states,
            attention_mask=attention_mask,
            position_bias=position_bias,
            layer_head_mask=layer_head_mask,
            past_key_value=self_attn_past_key_value,
            use_cache=use_cache
        )
        hidden_states, present_key_value_state = self_attention_outputs[:2]
        attention_outputs = self_attention_outputs[2:]  # Keep self-attention outputs and relative position weights

        # clamp inf values to enable fp16 training
        if torch.isinf(hidden_states).any():
            clamp_value = torch.finfo(hidden_states.dtype).max - 1000
            hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)

        do_cross_attention = self.is_decoder and encoder_hidden_states is not None
        if do_cross_attention:
            # the actual query length is unknown for cross attention
            # if using past key value states. Need to inject it here
            query_length = None if present_key_value_state is None else present_key_value_state[0].shape[2]

            cross_attention_outputs = self.layer[1](
                hidden_states,
                key_value_states=encoder_hidden_states,
                attention_mask=encoder_attention_mask,
                position_bias=encoder_decoder_position_bias,
                layer_head_mask=encoder_layer_head_mask,
                past_key_value=cross_attn_past_key_value,
                query_length=query_length,
                use_cache=use_cache
            )
            hidden_states = cross_attention_outputs[0]
            if torch.isinf(hidden_states).any():
                clamp_value = torch.finfo(hidden_states.dtype).max - 1000
                hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)

            # Combine self attn and cross attn key value states
            if present_key_value_state is not None:
                present_key_value_state = present_key_value_state + cross_attention_outputs[1]

            # Keep cross-attention outputs and relative position weights
            attention_outputs = attention_outputs + cross_attention_outputs[2:]

        # Apply Feed Forward layer
        hidden_states = self.layer[-1](hidden_states)
        if torch.isinf(hidden_states).any():
            clamp_value = torch.finfo(hidden_states.dtype).max - 1000
            hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)

        return (hidden_states, present_key_value_state) + attention_outputs


class T5Stack(torch.nn.Module):
    def __init__(self, config: dict, embed_tokens=None):
        super().__init__()

        self.embed_tokens = embed_tokens
        self.is_decoder = config['is_decoder']

        self.block = nn.ModuleList(
            T5Block(config, has_relative_attention_bias=(i == 0)) for i in range(config['num_layers'])
        )
        self.final_layer_norm = T5LayerNorm(config['d_model'], eps=config['layer_norm_epsilon'])
        self.use_cache = config['use_cache']
        self.use_return_dict = True
        self.num_layers = config['num_layers']

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        encoder_hidden_states=None,
        encoder_attention_mask=None,
        past_key_values=None,
        use_cache=None,
        return_dict=None
    ):
        use_cache = use_cache if use_cache is not None else self.use_cache
        return_dict = return_dict if return_dict is not None else self.use_return_dict

        input_shape = input_ids.size()
        input_ids = input_ids.view(-1, input_shape[-1])
        hidden_states = self.embed_tokens(input_ids)

        batch_size, seq_length = input_shape

        # required mask seq length can be calculated via length of past
        mask_seq_length = past_key_values[0][0].shape[2] + seq_length if past_key_values is not None else seq_length

        attention_mask = torch.ones(batch_size, mask_seq_length).to(hidden_states.device)
        if self.is_decoder and encoder_attention_mask is None and encoder_hidden_states is not None:
            encoder_seq_length = encoder_hidden_states.shape[1]
            encoder_attention_mask = torch.ones(
                batch_size, encoder_seq_length, device=hidden_states.device, dtype=torch.long
            )

        # initialize past_key_values with `None` if past does not exist
        if past_key_values is None:
            past_key_values = [None] * len(self.block)

        # ourselves in which case we just need to make it broadcastable to all heads.
        extended_attention_mask = self.get_extended_attention_mask(attention_mask, input_shape, hidden_states.device)

        encoder_extended_attention_mask = (
            self.invert_attention_mask(encoder_attention_mask)
            if self.is_decoder and encoder_attention_mask is not None else None
        )

        present_key_value_states = () if use_cache else None
        position_bias = None
        encoder_decoder_position_bias = None

        for layer_module, past_key_value in zip(self.block, past_key_values):
            layer_outputs = layer_module(
                hidden_states,
                attention_mask=extended_attention_mask,
                position_bias=position_bias,
                encoder_hidden_states=encoder_hidden_states,
                encoder_attention_mask=encoder_extended_attention_mask,
                encoder_decoder_position_bias=encoder_decoder_position_bias,
                layer_head_mask=None,
                encoder_layer_head_mask=None,
                past_key_value=past_key_value,
                use_cache=use_cache
            )
            # layer_outputs is a tuple with:
            # hidden-states, key-value-states, (self-attention weights), (self-attention position bias),
            # (cross-attention weights), (cross-attention position bias)
            hidden_states, present_key_value_state, position_bias = layer_outputs[:3]

            # We share the position biases between the layers - the first layer store them
            # layer_outputs = hidden-states, key-value-states (self-attention weights),
            # (self-attention position bias), (cross-attention weights), (cross-attention position bias)
            if self.is_decoder and encoder_hidden_states is not None:
                encoder_decoder_position_bias = layer_outputs[3]
            # append next layer key value states
            if use_cache:
                present_key_value_states = present_key_value_states + (present_key_value_state,)

        hidden_states = self.final_layer_norm(hidden_states)

        if not return_dict:
            return tuple(v for v in (hidden_states, present_key_value_states) if v is not None)
        return BaseModelOutputWithPastAndCrossAttentions(
            last_hidden_state=hidden_states, past_key_values=present_key_value_states
        )

    def get_extended_attention_mask(
            self, attention_mask: torch.Tensor, input_shape: Tuple[int, int], device: torch.device) -> torch.Tensor:
        # We can provide a self-attention mask of dimensions [batch_size, from_seq_length, to_seq_length]
        # ourselves in which case we just need to make it broadcastable to all heads.
        extended_attention_mask = attention_mask.unsqueeze(1)
        if attention_mask.dim() == 2:
            # Provided a padding mask of dimensions [batch_size, seq_length]
            # - if the model is a decoder, apply a causal mask in addition to the padding mask
            # - if the model is an encoder,
            # make the mask broadcastable to [batch_size, num_heads, seq_length, seq_length]
            extended_attention_mask = extended_attention_mask.unsqueeze(1)
            if self.is_decoder:
                batch_size, seq_length = input_shape
                seq_ids = torch.arange(seq_length, device=device).unsqueeze(0)
                causal_mask: torch.Tensor = seq_ids.unsqueeze(0).repeat(batch_size, seq_length, 1) <= seq_ids.unsqueeze(-1)
                # in case past_key_values are used we need to add a prefix ones mask to the causal mask
                # causal and attention masks must have same type with pytorch version < 1.3
                causal_mask = causal_mask.to(attention_mask.dtype)

                if causal_mask.shape[1] < attention_mask.shape[1]:
                    prefix_seq_len = attention_mask.shape[1] - causal_mask.shape[1]
                    causal_mask = torch.cat([
                        torch.ones((batch_size, seq_length, prefix_seq_len), device=device, dtype=causal_mask.dtype),
                        causal_mask
                    ], axis=-1)

                extended_attention_mask = causal_mask.unsqueeze(1) * extended_attention_mask

        # Since attention_mask is 1.0 for positions we want to attend and 0.0 for
        # masked positions, this operation will create a tensor which is 0.0 for
        # positions we want to attend and -10000.0 for masked positions.
        # Since we are adding it to the raw scores before the softmax, this is
        # effectively the same as removing these entirely.
        return (1.0 - extended_attention_mask.to(dtype=next(self.parameters()).dtype)) * -10000.0

    def invert_attention_mask(self, encoder_attention_mask: torch.Tensor) -> torch.Tensor:
        encoder_extended_attention_mask = encoder_attention_mask.unsqueeze(1)

        if encoder_attention_mask.dim() == 2:
            encoder_extended_attention_mask = encoder_extended_attention_mask.unsqueeze(1)

        dtype = next(self.parameters()).dtype

        return (1 - encoder_extended_attention_mask.to(dtype=dtype)) * (-1e4 if dtype == torch.float16 else -1e9)


class ConfigNameSpace:
    def __init__(self, kwargs: dict):
        self.max_length = 20
        self.torchscript = kwargs.pop("torchscript", False)  # Only used by PyTorch models
        self.use_bfloat16 = kwargs.pop("use_bfloat16", False)
        self.tie_word_embeddings = kwargs.pop("tie_word_embeddings", True)

        # Is decoder is used in encoder-decoder models to differentiate encoder from decoder
        self.is_encoder_decoder = kwargs.pop("is_encoder_decoder", True)
        self.is_decoder = kwargs.pop("is_decoder", False)
        self.add_cross_attention = kwargs.pop("add_cross_attention", False)
        self.tie_encoder_decoder = kwargs.pop("tie_encoder_decoder", False)

        # Parameters for sequence generation
        self.max_length = kwargs.pop("max_length", 20)
        self.min_length = kwargs.pop("min_length", 0)
        self.do_sample = kwargs.pop("do_sample", False)
        self.early_stopping = kwargs.pop("early_stopping", False)
        self.num_beams = kwargs.pop("num_beams", 1)
        self.num_beam_groups = kwargs.pop("num_beam_groups", 1)
        self.diversity_penalty = kwargs.pop("diversity_penalty", 0.0)
        self.temperature = kwargs.pop("temperature", 1.0)
        self.top_k = kwargs.pop("top_k", 50)
        self.top_p = kwargs.pop("top_p", 1.0)
        self.repetition_penalty = kwargs.pop("repetition_penalty", 1.0)
        self.length_penalty = kwargs.pop("length_penalty", 1.0)
        self.no_repeat_ngram_size = kwargs.pop("no_repeat_ngram_size", 0)
        self.encoder_no_repeat_ngram_size = kwargs.pop("encoder_no_repeat_ngram_size", 0)
        self.bad_words_ids = kwargs.pop("bad_words_ids", None)
        self.num_return_sequences = kwargs.pop("num_return_sequences", 1)
        self.chunk_size_feed_forward = kwargs.pop("chunk_size_feed_forward", 0)
        self.output_scores = kwargs.pop("output_scores", False)
        self.return_dict_in_generate = kwargs.pop("return_dict_in_generate", False)

        self.pad_token_id = 0
        self.eos_token_id = 1
        self.bos_token_id = None
        self.use_cache = kwargs.pop("use_cache", True)
        self.decoder_start_token_id = kwargs.pop('decoder_start_token_id')

        self.forced_bos_token_id = None
        self.forced_eos_token_id = None
        self.remove_invalid_values = None

        self.output_attentions = None
        self.output_hidden_states = None


class T5ForConditionalGeneration(torch.nn.Module, GenerationMixin):
    def __init__(self, config: dict):
        super().__init__()
        self.config = ConfigNameSpace(config)
        self.model_dim = config['d_model']

        self.shared = nn.Embedding(config['vocab_size'], config['d_model'])

        encoder_config = copy.deepcopy(config)
        encoder_config['is_decoder'] = False
        encoder_config['use_cache'] = False
        encoder_config['is_encoder_decoder'] = False
        self.encoder = T5Stack(encoder_config, self.shared)

        decoder_config = copy.deepcopy(config)
        decoder_config['is_decoder'] = True
        decoder_config['is_encoder_decoder'] = False
        decoder_config['num_layers'] = config['num_decoder_layers']
        decoder_config['use_cache'] = True

        self.decoder = T5Stack(decoder_config, self.shared)
        self.lm_head = Linear(config['d_model'], config['vocab_size'], bias=False)

        self.num_layers = config['num_layers']
        self.num_decoder_layers = config['num_decoder_layers']
        self.use_cache = True
        self.use_return_dict = True
        self.tie_word_embeddings = True

    @classmethod
    def from_pretrained(cls, model_path: str):
        with open(os.path.join(model_path, 'config.json'), 'r') as file:
            config = json.load(file)
        model = cls(config)
        state_dict = torch.load(os.path.join(model_path, 'pytorch_model.bin'), map_location='cpu')
        state_dict.pop('decoder.block.0.layer.1.EncDecAttention.relative_attention_bias.weight', None)
        model.load_state_dict(state_dict)
        return model

    def forward(
        self,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        encoder_outputs=None,
        past_key_values=None,
        return_dict=None,
        output_hidden_states=None,
        output_attentions=None
    ):
        if return_dict is None:
            return_dict = self.use_return_dict

        # Encode if needed (training, first prediction pass)
        if return_dict and not isinstance(encoder_outputs, BaseModelOutput):
            encoder_outputs = BaseModelOutput(last_hidden_state=encoder_outputs[0])

        hidden_states = encoder_outputs[0]

        # If decoding with past key value states, only the last tokens
        # should be given as an input
        if past_key_values is not None:
            if decoder_input_ids is not None:
                decoder_input_ids = decoder_input_ids[:, -1:]

        # Decode
        decoder_outputs = self.decoder(
            input_ids=decoder_input_ids,
            attention_mask=decoder_attention_mask,
            past_key_values=past_key_values,
            encoder_hidden_states=hidden_states,
            encoder_attention_mask=attention_mask,
            use_cache=True,
            return_dict=return_dict
        )

        sequence_output = decoder_outputs[0]

        if self.tie_word_embeddings:
            sequence_output = sequence_output * (self.model_dim ** -0.5)

        lm_logits = self.lm_head(sequence_output)

        if not return_dict:
            return (lm_logits,) + decoder_outputs[1:] + encoder_outputs

        return Seq2SeqLMOutput(
            logits=lm_logits,
            past_key_values=decoder_outputs.past_key_values,
            encoder_last_hidden_state=encoder_outputs.last_hidden_state
        )

    @staticmethod
    def prepare_inputs_for_generation(
        input_ids, past=None, attention_mask=None, use_cache=None, encoder_outputs=None, **kwargs
    ):

        # cut decoder_input_ids if past is used
        if past is not None:
            input_ids = input_ids[:, -1:]

        return {
            "decoder_input_ids": input_ids,
            "past_key_values": past,
            "encoder_outputs": encoder_outputs,
            "attention_mask": attention_mask
        }

    def _prepare_encoder_decoder_kwargs_for_generation(self, input_ids: torch.Tensor, model_kwargs) -> Dict[str, Any]:
        model_kwargs["encoder_outputs"] = self.encoder(input_ids, return_dict=True)
        return model_kwargs
