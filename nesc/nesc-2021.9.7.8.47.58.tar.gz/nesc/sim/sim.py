#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : sim_app
# @Time         : 2021/9/1 下午2:45
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.log_utils import logger4wecom
from meutils.decorators.catch import wecom_catch, wecom_hook

from bertzoo.simbert2vec import Simbert2vec
from gensim.models import KeyedVectors

s2v = Simbert2vec('chinese_roformer-sim-char-ft_L-6_H-384_A-6')

@lru_cache()
def text2vec(text='年收入'):
    return s2v.encoder([text], output_dim=None)[0]

def get_vector_cache():
    p = Path('vecs.cache')
    w2v = {}

    if p.is_file():
        for r in Path('vecs.cache').read_text().strip().split('\n'):
            r = r.split()
            w2v[r[0]] = np.array(r[1:], float)
    return w2v


s2v.encoder()

Path('vec.cache').read_text()


model = KeyedVectors.load_word2vec_format('vecs.txt', no_header=True)

text2score = model.similar_by_vector(text2vec(text), topn=topn)

df = pd.DataFrame(text2score, columns=['text', 'score'])
