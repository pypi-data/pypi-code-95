from typing import List

import numpy as np
import math


def calc_cos_sim(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """计算两个列向量之间的余弦相似度"""
    num = np.sum(vector_a * vector_b)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denom == 0:  # 任何一个向量的模为0时直接返回0，防止返回Nan
        return 0.0
    cos = num / denom
    return cos


def calc_idf(word: str, all_docs: List[str]) -> float:
    """计算某个word相对于多篇文章的IDF值"""
    idf = math.log(len(all_docs) / (1 + len([doc for doc in all_docs if word in doc])))
    return idf

