import torch
import torch.nn as nn


def _make_sequence(max_src_len, vocab_size, total, padding_idx=0):
    pass


def make_fake_feature_regression(feature_size, batch_size, total, tgt_range):
    pass


def make_fake_feature_classification(
    input_size, num_classes, batch_size, total, padding_idx=0,
):
    pass


def make_fake_text_classification(
    max_src_len, vocab_size, num_classes, batch_size, total, padding_idx=0,
):
    pass


def make_fake_sequence_labling(
    max_src_len, vocab_size, tag_size, batch_size, total,
    padding_idx=0,
):
    pass


def make_fake_seq2seq(
    max_src_len, max_tgt_len, vocab_size, batch_size, total, padding_idx=0,
):
    pass
