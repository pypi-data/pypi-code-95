#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : sim_app
# @Time         : 2021/9/1 下午2:45
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :


from shutil import copyfile

from meutils.pipe import *

from meutils.log_utils import logger4wecom
from meutils.decorators.catch import wecom_catch, wecom_hook
from meutils.annzoo.ann_faiss import ANN

from bertzoo.simbert2vec import Simbert2vec
from gensim.models import KeyedVectors

tqdm.pandas()

CACHE = 'cache.pkl'


def get_vector_cache(backup=False):
    p = Path(CACHE)  # p.read_text() windows有编码问题

    w2v = {}
    if p.is_file():
        if backup:
            copyfile(p, f"{p}.bak.{time.time()}")  # 备份cache

        w2v = joblib.load(CACHE)

    return w2v


def get_word_set(path):
    if Path(path).is_file():
        return set(pd.read_csv(path, names=['w']).w.astype(str).str.strip().str.replace('\t', ''))
    return {path}


def bert_vector(s1, s2, batch_size=3, model_home='chinese_roformer-sim-char-ft_L-6_H-384_A-6'):
    w2v = get_vector_cache()
    s = (s1 | s2) - set(w2v)

    if s:
        s2v = Simbert2vec(model_home)

        for ws in tqdm(list(s) | xgroup(batch_size), '向量化'):
            vs = s2v.encoder(ws, output_dim=None)
            w2v.update(zip(ws, vs))  # 向量全集

        joblib.dump(w2v, 'cache.pkl')  # 更新cache

    return w2v


def get_i2w_vecs(s, w2v):  # i2w, vecs/data
    s = list(s)
    i2w = dict(enumerate(s))
    v = operator.itemgetter(*s)(w2v)

    if len(s) > 1:
        return i2w, np.row_stack(v)
    else:
        return i2w, v.reshape(1, -1)


def get_rst(i2w_1, i2w_2, diss, idxs):
    dfs = []
    for idx, _ in enumerate(zip(diss, idxs)):  # 第idx个目标词
        i2s = dict(zip(*_[::-1]))

        w2s = [(i2w_2.get(i), s) for i, s in i2s.items() if i != -1]

        df = pd.DataFrame(w2s)
        df.insert(0, 'target', i2w_1.get(idx))
        dfs.append(df)
        break

    return pd.concat(dfs)


def main(target, file, topn=10, batch_size=512, model_home='chinese_roformer-sim-char-ft_L-6_H-384_A-6'):
    s1 = get_word_set(target)
    s2 = get_word_set(file)

    w2v = bert_vector(s1, s2, batch_size, model_home)

    i2w_1, data1 = get_i2w_vecs(s1, w2v)
    i2w_2, data2 = get_i2w_vecs(s2, w2v)

    ann = ANN()
    ann.train(data2, metric=0)
    diss, idxs = ann.search(data1, topn)

    df_rst = get_rst(i2w_1, i2w_2, diss, idxs)

    opath = Path(file).parent / 'recall.tsv'
    df_rst.to_csv(opath, '\t', index=False, header=False)
    logger.info(f"输出路径：{opath}")

    if len(s1) == 1:
        df_rst.columns = ['target', 'recall', 'score']
        tb = Besttable.draw_df(df_rst)
        time.sleep(0.3)
        print(tb)

    return df_rst
