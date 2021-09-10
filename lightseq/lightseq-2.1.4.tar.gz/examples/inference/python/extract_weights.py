import os
import math
from collections import OrderedDict

import numpy as np
import torch
import tensorflow as tf
from transformer_pb2 import Transformer

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
LANG2ID = {
    'af': 0, 'als': 1, 'am': 2, 'an': 3, 'ang': 4, 'ar': 5, 'arz': 6, 'ast': 7, 'az': 8, 'bar': 9, 
    'be': 10, 'bg': 11, 'bn': 12, 'br': 13, 'bs': 14, 'ca': 15, 'ceb': 16, 'ckb': 17, 'cs': 18, 'cy': 19, 
    'da': 20, 'de': 21, 'el': 22, 'en': 23, 'eo': 24, 'es': 25, 'et': 26, 'eu': 27, 'fa': 28, 'fi': 29, 
    'fr': 30, 'fy': 31, 'ga': 32, 'gan': 33, 'gl': 34, 'gu': 35, 'he': 36, 'hi': 37, 'hr': 38, 'hu': 39, 
    'hy': 40, 'ia': 41, 'id': 42, 'is': 43, 'it': 44, 'ja': 45, 'jv': 46, 'ka': 47, 'kk': 48, 'kn': 49, 
    'ko': 50, 'ku': 51, 'la': 52, 'lb': 53, 'lt': 54, 'lv': 55, 'mk': 56, 'ml': 57, 'mn': 58, 'mr': 59, 
    'ms': 60, 'my': 61, 'nds': 62, 'ne': 63, 'nl': 64, 'nn': 65, 'no': 66, 'oc': 67, 'pl': 68, 'pt': 69, 
    'ro': 70, 'ru': 71, 'scn': 72, 'sco': 73, 'sh': 74, 'si': 75, 'simple': 76, 'sk': 77, 'sl': 78, 'sq': 79, 
    'sr': 80, 'sv': 81, 'sw': 82, 'ta': 83, 'te': 84, 'th': 85, 'tl': 86, 'tr': 87, 'tt': 88, 'uk': 89, 
    'ur': 90, 'uz': 91, 'vi': 92, 'war': 93, 'wuu': 94, 'yi': 95, 'zh': 96, 'zh_classical': 97, 'zh_min_nan': 98, 'zh_yue': 99
}

""" key是proto参数的值，value是一个强大的表达式，每个&&分割tensor name的匹配路径或表达式，每个匹配
路径的子pattern用空格分隔，表达式用expression_开头，可以对每个tensor进行单独操作，支持多个表达式。多个匹配路径
和表达式最后会concat，axis=-1 """
enc_layer_mapping_dict = OrderedDict(
    {
        "multihead_norm_scale": "layer_norm1 weight",
        "multihead_norm_bias": "layer_norm1 bias",
        "multihead_project_kernel_qkv": "attentions q_lin weight&&attentions k_lin weight&&attentions v_lin weight&&expression_.transpose(0, 1)",
        "multihead_project_bias_qkv": "attentions q_lin bias&&attentions k_lin bias&&attentions v_lin bias",
        "multihead_project_kernel_output": "attentions out_lin weight&&expression_.transpose(0, 1)",
        "multihead_project_bias_output": "attentions out_lin bias",
        "ffn_norm_scale": "layer_norm2 weight",
        "ffn_norm_bias": "layer_norm2 weight",
        "ffn_first_kernel": "lin1 weight&&expression_.transpose(0, 1)",
        "ffn_first_bias": "lin1 bias",
        "ffn_second_kernel": "lin2 weight&&expression_.transpose(0, 1)",
        "ffn_second_bias": "lin2 bias",
    }
)

dec_layer_mapping_dict = OrderedDict(
    {
        "self_norm_scale": "layer_norm1 weight",
        "self_norm_bias": "layer_norm1 bias",
        "self_project_kernel_qkv": "attentions q_lin weight&&attentions k_lin weight&&attentions v_lin weight&&expression_.transpose(0, 1)",
        "self_project_bias_qkv": "attentions q_lin bias&&attentions k_lin bias&&attentions v_lin bias",
        "self_project_kernel_output": "attentions out_lin weight&&expression_.transpose(0, 1)",
        "self_project_bias_output": "attentions out_lin bias",
        "encdec_norm_scale": "layer_norm15 weight",
        "encdec_norm_bias": "layer_norm15 bias",
        "encdec_project_kernel_q": "encoder_attn q_lin weight&&expression_.transpose(0, 1)",
        "encdec_project_bias_q": "encoder_attn q_lin bias",
        "encdec_project_kernel_output": "encoder_attn out_lin weight&&expression_.transpose(0, 1)",
        "encdec_project_bias_output": "encoder_attn out_lin bias",
        "ffn_norm_scale": "layer_norm2 weight",
        "ffn_norm_bias": "layer_norm2 bias",
        "ffn_first_kernel": "lin1 weight&&expression_.transpose(0, 1)",
        "ffn_first_bias": "lin1 bias",
        "ffn_second_kernel": "lin2 weight&&expression_.transpose(0, 1)",
        "ffn_second_bias": "lin2 bias",
    }
)

src_emb_mapping_dict = OrderedDict(
    {
        "norm_scale": "layer_norm_emb weight",
        "norm_bias": "layer_norm_emb bias",
    }
)

trg_emb_mapping_dict = OrderedDict(
    {
        "norm_scale": "layer_norm_emb weight",
        "norm_bias": "layer_norm_emb bias",
        "shared_bias": "pred_layer bias",
    }
)

shared_trg_emb_mapping_dict = OrderedDict(
    {
        "norm_scale": "layer_norm_emb weight",
        "norm_bias": "layer_norm_emb bias",
        "shared_bias": "pred_layer bias",
    }
)


def check_rule(tensor_name, rule):
    if "Adam" in tensor_name or "adam" in tensor_name:
        return False
    assert isinstance(rule, str) and rule
    rule = rule.split("-")
    assert len(rule) < 3
    if len(rule) == 2:
        white, black = rule[0].split(" "), rule[1].split(" ")
    else:
        white, black = rule[0].split(" "), []
    for b in black:
        if b in tensor_name.split("."):
            return False
    for w in white:
        if w not in tensor_name.split("."):
            return False
    return True


def fill_layer(tensor_names, stete_dict, layer, mapping_dict):
    for proto_name, ckpt_rule in mapping_dict.items():
        expression = [
            ele for ele in ckpt_rule.split("&&") if ele.startswith("expression_")
        ]

        ckpt_rule = [
            ele for ele in ckpt_rule.split("&&") if not ele.startswith("expression_")
        ]

        assert (len(ckpt_rule) > 0 and len(expression) < 2) or (
            len(ckpt_rule) == 0 and len(expression) > 0
        )

        if len(expression) < 2:
            expression = "" if not expression else expression[0].split("_")[1]
        else:
            expression = [exp.split("_")[1] for exp in expression]

        target_tn = []
        for cr in ckpt_rule:
            tmp = []
            for tn in tensor_names:
                if check_rule(tn, cr):
                    tmp.append(tn)
            if len(tmp) != 1:
                print("not equal 1")
                print(tmp)
            assert len(tmp) == 1
            target_tn.extend(tmp)
        target_tensor = [stete_dict[name] for name in target_tn]
        tt = {}
        if target_tensor:
            exec("tt['save'] = [ele%s for ele in target_tensor]" % expression)
        else:
            if not isinstance(expression, list):
                expression = [expression]
            exec("tt['save'] = [%s]" % ",".join(expression))

        target_tensor = np.concatenate(tt["save"], axis=-1)
        print(
            "%s -> %s, shape: %s, convert finished."
            % (target_tn if target_tn else "created", proto_name, target_tensor.shape)
        )
        exec("layer.%s[:]=target_tensor.flatten().tolist()" % proto_name)


def _get_encode_output_mapping_dict(dec_layer_num):
    encode_output_kernel_pattern = [
        "encoder_attn {0} k_lin weight&&encoder_attn {0} v_lin weight".format(ele)
        for ele in range(dec_layer_num)
    ]
    encode_output_bias_pattern = [
        "encoder_attn {0} k_lin bias&&encoder_attn {0} v_lin bias".format(ele)
        for ele in range(dec_layer_num)
    ]

    return {
        "encode_output_project_kernel_kv": "&&".join(
            encode_output_kernel_pattern + ["expression_.transpose(0, 1)"]
        ),
        "encode_output_project_bias_kv": "&&".join(encode_output_bias_pattern),
    }


def _get_position_encoding(length, hidden_size, min_timescale=1.0, max_timescale=1.0e4):
    """Return positional encoding.

    Calculates the position encoding as a mix of sine and cosine functions with
    geometrically increasing wavelengths.
    Defined and formulized in Attention is All You Need, section 3.5.

    Args:
      length: Sequence length.
      hidden_size: Size of the
      min_timescale: Minimum scale that will be applied at each position
      max_timescale: Maximum scale that will be applied at each position

    Returns:
      Tensor with shape [length, hidden_size]
    """
    with tf.device("/cpu:0"):
        position = tf.cast(tf.range(length), tf.float32)
        num_timescales = hidden_size // 2
        log_timescale_increment = math.log(
            float(max_timescale) / float(min_timescale)
        ) / (tf.cast(num_timescales, tf.float32) - 1)
        inv_timescales = min_timescale * tf.exp(
            tf.cast(tf.range(num_timescales), tf.float32) * -log_timescale_increment
        )
        scaled_time = tf.expand_dims(position, 1) * tf.expand_dims(inv_timescales, 0)
        signal = tf.concat([tf.math.sin(scaled_time), tf.math.cos(scaled_time)], axis=1)
    return signal


def _gather_token_embedding(tensor_names, name2var_dict, tn_pattern, lang="en"):
    """ use pattern to diff source and target. """
    target_tn = []
    lang_embedding = None
    for tn in tensor_names:
        if (tn_pattern in tn.split(".")) and ("weight" in tn.split(".")):
            target_tn.append(tn)
            continue
        if tn == "lang_embeddings.weight":
            lang_embedding = name2var_dict[tn].numpy()
    # target_tn = sorted(target_tn, key=lambda x: int(x.split('_')[-1]))
    # print(target_tn)
    target_tensor = [name2var_dict[name] for name in target_tn]
    target_tensor = np.concatenate(target_tensor, axis=0)
    # target_tensor = target_tensor * (target_tensor.shape[1] ** 0.5)
    print(
        "lang embedding shape: {}, added {} embedding to token embeddings".format(
            lang, lang_embedding.shape
        )
    )
    target_tensor += lang_embedding[LANG2ID[lang]]
    print("token embedding shape is {}".format(target_tensor.shape))
    # print("token embedding shape is %s" % target_tensor.shape)

    return target_tensor


def extract_transformer_weights(
    output_file,
    model_dir,
    head_num,
    generation_method,
    max_step,
    extra_decode_length=50,
    beam_size=4,
    length_penalty=0,
    topk=4,
    topp=0.75,
    lang="en",
    only_decoder=True,
):
    transformer = Transformer()
    # load var names
    reloaded = torch.load(model_dir, "cpu")
    print(reloaded.keys())
    decoder_state_dict = reloaded["decoder"]
    encoder_state_dict = reloaded["encoder"]
    dec_var_name_list = list(decoder_state_dict.keys())
    enc_var_name_list = list(encoder_state_dict.keys())

    # print(decoder_state_dict.keys())
    # print(decoder_state_dict["module.embeddings.weight"].numpy().shape[0]) # 20,0000
    trg_emb_mapping_dict["shared_bias"] = (
        "expression_np.zeros(%d)"
        % decoder_state_dict["module.embeddings.weight"].numpy().shape[0]
    )

    # fill each encoder  layer's params
    if not only_decoder:
        enc_tensor_names = {}
        for name in enc_var_name_list:
            if not name.split(".")[1].isdigit():
                continue
            layer_id = int(name.split(".")[1])
            enc_tensor_names.setdefault(layer_id, []).append(name)

        for layer_id in sorted(enc_tensor_names.keys()):
            fill_layer(
                enc_tensor_names[layer_id],
                encoder_state_dict,
                transformer.encoder_stack.add(),
                enc_layer_mapping_dict,
            )

    # fill each decoder layer's params
    dec_tensor_names = {}
    for name in dec_var_name_list:
        if not name.split(".")[1].isdigit():
            continue
        layer_id = int(name.split(".")[1])
        dec_tensor_names.setdefault(layer_id, []).append(name)

    for layer_id in sorted(dec_tensor_names.keys()):
        fill_layer(
            dec_tensor_names[layer_id],
            decoder_state_dict,
            transformer.decoder_stack.add(),
            dec_layer_mapping_dict,
        )

    # fill src_embedding
    if not only_decoder:
        fill_layer(
            enc_var_name_list,
            encoder_state_dict,
            transformer.src_embedding,
            src_emb_mapping_dict,
        )
        pos_emb_list = (
            encoder_state_dict["position_embeddings.weight"]
            .numpy()[:max_step, :]
            .reshape([-1])
            .tolist()
        )
        transformer.src_embedding.position_embedding[:] = pos_emb_list
        print(
            "position_embeddings.weight -> src_embedding.position_embedding, shape: {}, conversion finished!".format(
                encoder_state_dict["position_embeddings.weight"]
                .numpy()[:max_step, :]
                .shape
            )
        )
        src_tb = _gather_token_embedding(
            enc_var_name_list, encoder_state_dict, "embeddings"
        )
        transformer.src_embedding.token_embedding[:] = src_tb.flatten().tolist()

    # fill trg_embedding
    encode_output_mapping_dict = _get_encode_output_mapping_dict(len(dec_tensor_names))
    trg_emb_mapping_dict.update(encode_output_mapping_dict)
    fill_layer(
        dec_var_name_list,
        decoder_state_dict,
        transformer.trg_embedding,
        trg_emb_mapping_dict,
    )
    pos_emb_list = (
        decoder_state_dict["position_embeddings.weight"]
        .numpy()[:max_step, :]
        .reshape([-1])
        .tolist()
    )
    transformer.trg_embedding.position_embedding[:] = pos_emb_list
    print(
        "position_embeddings.weight -> trg_embedding.position_embedding, shape: {}, conversion finished!".format(
            decoder_state_dict["position_embeddings.weight"].numpy()[:max_step, :].shape
        )
    )
    assert lang in LANG2ID
    trg_tb = _gather_token_embedding(
        dec_var_name_list, decoder_state_dict, "embeddings", lang=lang
    )
    transformer.trg_embedding.token_embedding[:] = trg_tb.transpose().flatten().tolist()
    print(
        "token_embedding.weight -> trg_embedding.token_embedding, shape: {}, conversion finished!".format(
            trg_tb.transpose().shape
        )
    )

    # change layer norm scale&bias position
    tmp_scale, tmp_bias = (
        transformer.trg_embedding.norm_scale,
        transformer.trg_embedding.norm_bias,
    )
    for i, decoder in enumerate(transformer.decoder_stack):
        print("Fix layer {} LayerNorm scale and bias.".format(i))
        new_tmp_scale, new_tmp_bias = (
            decoder.self_norm_scale[:],
            decoder.self_norm_bias[:],
        )
        decoder.self_norm_scale[:], decoder.self_norm_bias[:] = tmp_scale, tmp_bias
        print(
            "self_norm_scale: {} -> {}\nself_norm_bias: {} -> {}".format(
                new_tmp_scale[:3],
                decoder.self_norm_scale[:3],
                new_tmp_bias[:3],
                decoder.self_norm_bias[:3],
            )
        )
        tmp_scale, tmp_bias = new_tmp_scale[:], new_tmp_bias[:]

        new_tmp_scale, new_tmp_bias = (
            decoder.encdec_norm_scale[:],
            decoder.encdec_norm_bias[:],
        )
        decoder.encdec_norm_scale[:], decoder.encdec_norm_bias[:] = tmp_scale, tmp_bias
        print(
            "encdec_norm_scale: {} -> {}\nencdec_norm_bias: {} -> {}".format(
                new_tmp_scale[:3],
                decoder.encdec_norm_scale[:3],
                new_tmp_bias[:3],
                decoder.encdec_norm_bias[:3],
            )
        )
        tmp_scale, tmp_bias = new_tmp_scale[:], new_tmp_bias[:]

        new_tmp_scale, new_tmp_bias = (
            decoder.ffn_norm_scale[:],
            decoder.ffn_norm_bias[:],
        )
        decoder.ffn_norm_scale[:], decoder.ffn_norm_bias[:] = (
            tmp_scale,
            tmp_bias,
        )
        print(
            "ffn_norm_scale: {} -> {}\nffn_norm_bias: {} -> {}".format(
                new_tmp_scale[:3],
                decoder.ffn_norm_scale[:3],
                new_tmp_bias[:3],
                decoder.ffn_norm_bias[:3],
            )
        )
        tmp_scale, tmp_bias = new_tmp_scale[:], new_tmp_bias[:]
    transformer.trg_embedding.norm_scale[:], transformer.trg_embedding.norm_bias[:] = (
        tmp_scale,
        tmp_bias,
    )

    # fill in conf

    transformer.model_conf.head_num = head_num

    transformer.model_conf.beam_size = beam_size
    transformer.model_conf.length_penalty = length_penalty

    transformer.model_conf.extra_decode_length = extra_decode_length
    transformer.model_conf.src_padding_id = 2
    transformer.model_conf.trg_start_id = 1
    transformer.model_conf.trg_end_id = 1

    transformer.model_conf.sampling_method = generation_method
    transformer.model_conf.topk = topk
    transformer.model_conf.topp = topp
    transformer.model_conf.diverse_lambda = 0
    transformer.model_conf.is_post_ln = True
    transformer.model_conf.no_scale_embedding = True
    transformer.model_conf.use_gelu = True

    print("Wrting to {0}".format(output_file))
    with tf.io.gfile.GFile(output_file, "wb") as fout:
        fout.write(transformer.SerializeToString())

    transformer = Transformer()
    with tf.io.gfile.GFile(output_file, "rb") as fin:
        transformer.ParseFromString(fin.read())
    print(transformer.model_conf)


if __name__ == "__main__":
    # sampling
    # extract_transformer_weights(
    #     "./../models/multilingual_title_en_decoder_sampling_new.pb",
    #     "./../models/best_en-en_Bleu_4.pth",
    #     8,
    #     "topp",
    #     beam_size=32,
    #     max_step=64,
    #     lang="en",
    # )

    # topk greedy
    extract_transformer_weights(
        "multilingual_title_de_greedy_v1.pb",
        "best_de-de_Bleu_4.pth",
        16,
        "topk_greedy",
        beam_size=32,
        max_step=32,
        lang="de",
    )
