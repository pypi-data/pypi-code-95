#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : Bert
# @Time         : 2020/11/20 2:59 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from meutils.np_utils import normalize
from meutils.path_utils import get_module_path
from bertzoo.utils.bert4keras_utils import *


class Simbert2vec(object):

    def __init__(self, bert_home=None):
        """
        '/fds/data/bert/chinese_simbert_L-12_H-768_A-12/vocab.txt'
        :param dict_path:
        :param config_path:
        :param checkpoint_path:
        """
        if bert_home is None:
            bert_home = get_module_path(f'./data/chinese_simbert_L-4_H-312_A-12', __file__)

        model_name = 'roformer' if 'roformer' in bert_home else 'bert'

        self.dict_path = f"{bert_home}/vocab.txt"
        self.config_path = f"{bert_home}/bert_config.json"
        self.checkpoint_path = f"{bert_home}/bert_model.ckpt"

        print(self.dict_path)

        self.tokenizer = Tokenizer(self.dict_path, do_lower_case=True)

        # 建立加载模型
        logger.info("BuildingModel")
        self._bert = build_transformer_model(
            self.config_path,
            self.checkpoint_path,
            model=model_name,
            with_pool='linear',
            application='unilm',
            return_keras_model=False  # True: bert.predict([np.array([token_ids]), np.array([segment_ids])])
        )

        self._encoder = keras.models.Model(self._bert.model.inputs, self._bert.model.outputs[0])
        # self._seq2seq = keras.models.Model(self._bert.model.inputs, self._bert.model.outputs[1])

    def encoder(self, texts=None, output_dim=768 / 4):
        data = texts2seq(texts=texts, tokenizer=self.tokenizer)
        vecs = self._encoder.predict(data, batch_size=1000)

        if output_dim == 768 / 4:
            vecs = vecs[:, range(0, 768, 4)]
        elif output_dim == 768 / 3:
            vecs = vecs[:, range(0, 768, 3)]

        return normalize(vecs)


if __name__ == '__main__':
    BERT_HOME = "/Users/yuanjie/Downloads/chinese_roformer-sim-char-ft_L-6_H-384_A-6"

    s2v = Simbert2vec(BERT_HOME)

    print(s2v.encoder(['笨蛋'], output_dim=None))
