#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : Bert
# @Time         : 2020/11/20 2:59 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from bertzoo.utils.bert4keras_utils import *


# todo: 增加推理
class SimBert(object):

    def __init__(self, dict_path=None, config_path=None, checkpoint_path=None):
        """
        '/fds/data/bert/chinese_simbert_L-12_H-768_A-12/vocab.txt'
        :param dict_path:
        :param config_path:
        :param checkpoint_path:
        """
        if dict_path is None:
            p = get_module_path(f'../data/chinese_simbert_L-4_H-312_A-12.zip')
            target = Path(p).parent / 'chinese_simbert_L-4_H-312_A-12'

            os.system(f'cd {target} && unzip {p}')

            dict_path = str(dict_path / 'vocab.txt')

        top_dir = Path(dict_path).parent
        if config_path is None:
            config_path = str(top_dir / 'bert_config.json')
        if checkpoint_path is None:
            checkpoint_path = str(top_dir / 'bert_model.ckpt')

        self.dict_path = dict_path
        self.config_path = config_path
        self.checkpoint_path = checkpoint_path

        self.tokenizer = Tokenizer(dict_path, do_lower_case=True)

    @property
    def encoder(self, ):
        return keras.models.Model(self._bert.model.inputs, self._bert.model.outputs[0])

    @property
    def seq2seq(self, ):
        return keras.models.Model(self._bert.model.inputs, self._bert.model.outputs[1])

    def build_model(self):
        # 建立加载模型
        logger.info("Building model ...")
        self._bert = build_transformer_model(
            self.config_path,
            self.checkpoint_path,
            with_pool='linear',
            application='unilm',
            return_keras_model=False  # True: bert.predict([np.array([token_ids]), np.array([segment_ids])])
        )


class SynonymsGenerator(AutoRegressiveDecoder):
    """seq2seq解码器
    """

    def __init__(self, start_id=None, end_id=None, maxlen=64, tokenizer=None, seq2seq=None):
        super().__init__(start_id, end_id, maxlen)
        self.end_id = tokenizer._token_end_id
        self.tokenizer = tokenizer
        self.seq2seq = seq2seq

    @AutoRegressiveDecoder.wraps(default_rtype='probas')
    def predict(self, inputs, output_ids, states):
        token_ids, segment_ids = inputs
        token_ids = np.concatenate([token_ids, output_ids], 1)
        segment_ids = np.concatenate([segment_ids, np.ones_like(output_ids)], 1)
        return self.seq2seq.predict([token_ids, segment_ids])[:, -1]

    def generate(self, text, n=1, topp=0.95):
        token_ids, segment_ids = self.tokenizer.encode(text, maxlen=self.maxlen)
        output_ids = self.random_sample([token_ids, segment_ids], n,
                                        topp=topp)  # 基于随机采样
        return [self.tokenizer.decode(ids) for ids in output_ids]


if __name__ == '__main__':
    # sb = SimBert('/fds/data/bert/chinese_simbert_L-12_H-768_A-12/vocab.txt')
    # sb.build_model()
    #
    # tokenizer = sb.tokenizer
    # encoder = sb.encoder
    # seq2seq = sb.seq2seq
    #
    # sg = SynonymsGenerator(tokenizer=tokenizer, seq2seq=seq2seq)
    #
    #
    # def gen_synonyms(text, n=200, k=10):
    #     """"含义： 产生sent的n个相似句，然后返回最相似的k个。
    #     做法：用seq2seq生成，并用encoder算相似度并排序。
    #     """
    #     r = sg.generate(text, n)
    #     r = [i for i in set(r) if i != text]
    #     r = [text] + r
    #     X, S = [], []
    #     for t in r:
    #         x, s = tokenizer.encode(t)
    #         X.append(x)
    #         S.append(s)
    #     X = sequence_padding(X)
    #     S = sequence_padding(S)
    #     Z = encoder.predict([X, S])
    #     Z /= (Z ** 2).sum(axis=1, keepdims=True) ** 0.5
    #     argsort = np.dot(Z[1:], -Z[0]).argsort()
    #     return [r[i + 1] for i in argsort[:k]]
    #
    #
    # gen_synonyms('支付宝')
    SimBert()
