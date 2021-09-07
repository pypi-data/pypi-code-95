from typing import List
import logging
import math
from itertools import chain, combinations

import numpy as np
import pandas as pd
import xgboost as xgb

from ..api import BaseExplainer


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def explain_ref_reason_codes_xgb(x1, x2, RCs, model, margin):
    importance = {}
    # x2_mat = xgb.DMatrix(x2)
    weights = [0] * (len(RCs))
    for i in range(len(RCs)):
        weights[i] = 1 / (
            float(len(RCs)) *
            float(math.factorial(len(RCs) - 1) // (math.factorial(i) * math.factorial(len(RCs) - 1 - i)))
        )
    for rc in RCs:
        remaining_rcs = [c for c in RCs if not (c == rc)]
        importance[str(rc)] = 0
        powerset_it = powerset(remaining_rcs)
        for subset_S in powerset_it:
            x2_copy = x2.copy()
            for code in subset_S:
                x2_copy[code] = x1[code].values[0]
            x2_copy_col = x2_copy.copy()
            x2_copy_col[rc] = x1[rc].values[0]
            x2_copy_mat = xgb.DMatrix(x2_copy)
            x2_copy_col_mat = xgb.DMatrix(x2_copy_col)
            value = model.predict(x2_copy_col_mat,
                                  output_margin=margin) - model.predict(x2_copy_mat, output_margin=margin)
            weight = weights[len(subset_S)]
            importance[str(rc)] += (value * weight)
        importance[str(rc)] = (importance[str(rc)])[0]
    return importance


class ExponentialGroupTreeExplainer(BaseExplainer):
    def __init__(
        self,
        model,
        data,
        feature_groups: List[List[int]],
        model_output='raw',
    ):
        super().__init__(model)

        if model_output == 'raw':
            self.output_margin = True
        elif model_output == 'probability':
            self.output_margin = False
        else:
            raise ValueError('Invalid model_output')

        self.feature_groups = feature_groups
        self.data = self.preprocess(data)

    def shap_values(self, X):
        X = self.preprocess(X)

        codes = [[f"f{i}" for i in x] for x in self.feature_groups]
        return np.array(
            [
                np.array(
                    [
                        list(
                            explain_ref_reason_codes_xgb(
                                pd.DataFrame(x, index=[f'f{i}' for i in range(len(x))]).T,
                                pd.DataFrame(x_ref, index=[f'f{i}' for i in range(len(x))]).T,
                                RCs=codes,
                                model=self.model.booster,
                                margin=self.output_margin,
                            ).values()
                        ) for x_ref in self.data
                    ]
                ).mean(axis=0) for x in X
            ]
        )