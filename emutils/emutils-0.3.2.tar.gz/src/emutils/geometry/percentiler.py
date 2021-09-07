import logging
from typing import Union
import bisect

import numpy as np


class PercentileShifter:
    def __init__(self):
        pass

    def fit(self, X, y=None):
        X = np.asarray(X)
        # NOTE: self.data is transposed
        self.len = X.shape[0]
        self.data = np.sort(X, axis=0).T

        return self

    def get_percentile(self, x, f=None):
        if f is None:
            return self.get_sample_percentile(x)
        else:
            return self.get_feature_percentile(x, f)

    def get_shift(self, x, y):
        return np.abs(self.get_sample_percentile(x) - self.get_sample_percentile(y))

    def get_feature_percentile(self, vals, f):
        return np.array(
            [
                np.searchsorted(self.data[f], v, side='left') + np.searchsorted(self.data[f], v, side='right')
                for v in vals
            ]
        ) / self.len / 2

    def get_sample_percentile(self, x):
        return np.array(
            [
                np.searchsorted(self.data[f], xf, side='left') + np.searchsorted(self.data[f], xf, side='right')
                for f, xf in enumerate(x)
            ]
        ) / self.len / 2

    def shift_single_transform(self, x, indices=None, perc=.01):
        """Shift x features of a certain percentiles

        Args:
            x ([np.array]): the vector that need to be shifted
            indices ([Iterable]): The features (indices) that must be shifted
            perc ([float, Iterable], optional): The percentile shift(s). If iterable one per indices. Defaults to .01.

        Returns:
            [np.array]: Percentile shifted x
        """

        x_prime = x.copy()

        if indices is None:
            indices = np.arange(len(x))
        if isinstance(perc, (float, int)):
            perc = [perc] * len(indices)

        for f, p in zip(indices, perc):
            val = x[f]
            # Computer the percentile index averaging between left and right
            nb_lesser = (np.count_nonzero(self.data[f] <= val) + np.count_nonzero(self.data[f] < val)) / 2

            # Let's shift it
            newindex = int(np.round(max(
                min(
                    nb_lesser + p * self.len,
                    self.len - 1,
                ),
                0,
            )))
            # Get the value
            newval = self.data[f][newindex]
            # Change the x
            x_prime[f] = newval

        return x_prime

    def shift_transform(self, X, shifts):
        assert len(X) == len(shifts)
        assert len(shifts.shape == 2)
        X = np.asarray(X)

        ret = []
        for x, shift in zip(X, shifts):
            ret.append(self.shift_single_transform(x, shift=shift))
        return np.array(ret)

    def single_transform(self, x):
        return self.get_sample_percentile(x)

    def transform(self, X):
        X = np.asarray(X)
        return np.array([self.get_sample_percentile(x) for x in X])

    def inverse_transform(self, X):
        raise NotImplementedError('Inverse transformation is not implemented for percentiler shifter')


class PercentileShifterCached(PercentileShifter):
    def fit(self, *args, **kwargs):
        super().fit(*args, **kwargs)

        self.cache_values, self.cache_perc, self.cache_perc_mid = self._create_cache()

        return self

    def _create_cache(self):
        cache_values, cache_perc, cache_perc_mid = [], [], []
        logging.info('Building PercentileShifter cache...')
        for f, all_values in enumerate(self.data):
            # Values
            values = np.unique(all_values)
            cache_values.append(values)
            # Mid values
            values_mid = [values[0] - 1] + [(values[i - 1] + values[i]) / 2
                                            for i in range(1, len(values))] + [values[-1] + 1]
            # Percentile of values
            cache_perc.append(super().get_feature_percentile(values, f))
            # Percentile of mid values
            cache_perc_mid.append(super().get_feature_percentile(values_mid, f))
        logging.info('PercentileShifter cache built.')
        return cache_values, cache_perc, cache_perc_mid

    def __get_percentile(self, x, i):
        # Get array
        a_v = self.cache_values[i]

        j = bisect.bisect_left(a_v, x)
        if j >= len(a_v):
            return 1.0
        if x == a_v[j]:
            return self.cache_perc[i][j]
        else:
            return self.cache_perc_mid[i][j]

    def get_sample_percentile(self, x):
        return np.array([self.__get_percentile(v, i) for i, v in enumerate(x)])