#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : GPT
# @Time         : 2020/11/20 6:05 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import AutoRegressiveDecoder
# from bert4keras.snippets import uniout


class GPT2(object):

    def __init__(self, top_dir='/fds/data/bert/chinese_simbert_L-12_H-768_A-12'):
        top_dir = Path(top_dir)

        self.config_path = top_dir / 'config.json'
        self.checkpoint_path = top_dir / 'model.ckpt-100000'
        dict_path = top_dir / 'vocab.txt'

        self.tokenizer = Tokenizer(str(dict_path), token_start=None, token_end=None, do_lower_case=True)
        self.model = self.get_model()

    def get_model(self):
        model = build_transformer_model(
            config_path=str(self.config_path), checkpoint_path=str(self.checkpoint_path), model='gpt2_ml'
        )  # 建立模型，加载权重
        return model


class ArticleCompletion(AutoRegressiveDecoder):
    """基于随机采样的文章续写
    """

    def __init__(self, start_id, end_id, maxlen, minlen, model, tokenizer):
        super().__init__(start_id, end_id, maxlen, minlen)
        self.model = model
        self.tokenizer = tokenizer

    @AutoRegressiveDecoder.wraps(default_rtype='probas')
    def predict(self, inputs, output_ids, states):
        token_ids = np.concatenate([inputs[0], output_ids], 1)
        return self.model.predict(token_ids)[:, -1]

    def generate(self, text, n=1, topp=0.95):
        token_ids, _ = self.tokenizer.encode(text)
        results = self.random_sample([token_ids], n, topp=topp)  # 基于随机采样
        return [text + self.tokenizer.decode(ids) for ids in results]


if __name__ == '__main__':
    gpt = GPT2()

    article_completion = ArticleCompletion(
        start_id=None,
        end_id=511,  # 511是中文句号
        maxlen=256,
        minlen=128,
        model=gpt.model,
        tokenizer=gpt.tokenizer
    )

    print(article_completion.generate(u'今天天气不错'))
