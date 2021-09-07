import logging
from dataclasses import dataclass
from collections import defaultdict, Counter

import numpy as np
import pandas as pd

from emutils.utils import is_monotonic, random_stability, import_tqdm
from .decompose import splits_to_values

tqdm = import_tqdm()

LESS, MORE = '<', '>='


def get_feature_objects(splits, feature_names=None, feature_trends=None):
    if feature_names is None:
        feature_names = [None] * len(splits)

    if feature_trends is None:
        feature_trends = [None] * len(splits)

    values_left = splits_to_values(splits, how='left')
    values_center = splits_to_values(splits, how='center')
    values_right = splits_to_values(splits, how='right')

    objects = [
        Feature(
            idx=f,
            name=name,
            trend=trend,
            splits=split,
            values={
                -1: values_left[f],
                0: values_center[f],
                +1: values_right[f],
            },
        ) for f, (trend, name, split) in enumerate(zip(feature_trends, feature_names, splits))
    ]

    for i in range(len(objects)):
        assert objects[i].idx == i

    return objects


@dataclass
class Feature:
    def __init__(
        self,
        idx: int,
        trend: None,
        name: None = None,
        splits=None,
        values=None,
    ):
        self.idx = idx
        self.trend = trend
        self.name = name or str(idx)
        self.splits = splits
        self.values = values

    def set(self, **kwargs):
        return self.__dict__.update(kwargs)

    def get_values(self, which=0):
        if self.is_useless():
            logging.warning("This feature do not have any splits, using 0.")
        vid = int(-1 + np.heaviside(which, .5) * 2)
        return self.values[vid].copy()

    def get_values_towards_change(self, val, target_class=0):
        if self.is_useless():
            return np.array([])
        assert target_class in [0, 1]
        which = -1 * (target_class - .5) * self.trend
        feature_values = self.get_values(which=which)
        if which < 0:
            return np.array([v for v in feature_values if v > val])
        elif which > 0:
            return np.array([v for v in reversed(feature_values) if v < val])
        else:
            raise ValueError("Invalid value for which")

    def is_useless(self):
        return (len(self.splits) == 0)

    def __eq__(self, other):
        return self.idx == other.idx


def monotonicity_test(model, feature_values, random_state, nb_tests=10000):
    # Stabilize
    random_stability(random_state)

    X_random = np.vstack([np.random.choice(values, size=nb_tests) for values in feature_values]).T

    naive_monotonicity = defaultdict(list)
    for x in tqdm(X_random, desc='Monotonic test'):
        for f, values in enumerate(feature_values):
            X_prime = np.tile(x, (len(values), 1))
            for i, val in enumerate(values):
                X_prime[i][f] = val
            pred = model.predict_proba(X_prime)[:, 1]
            naive_monotonicity[f].append(is_monotonic(pred))

    for k, v in naive_monotonicity.items():
        naive_monotonicity[k] = np.all(np.array(v))

    counter = Counter(list(naive_monotonicity.values()))

    naive_monotonicity_stats = pd.DataFrame(
        {'Monotone' if k is True else 'Non-Monotone': [counter[k]]
         for k in [True, False]},
        index=['Number of features']
    ).T

    return naive_monotonicity_stats
