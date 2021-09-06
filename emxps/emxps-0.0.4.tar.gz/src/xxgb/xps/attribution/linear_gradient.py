import logging

import numpy as np
from tqdm import tqdm
from emutils.dsutils import process_data

from sklearn.linear_model import Ridge

from ..api import ModelWithDecisionFunction
from .api import BaseExplainer, BaseSupportsDynamicBackground

__all__ = ['LinearGradientExplainer']


class LinearGradientExplainer(BaseExplainer, BaseSupportsDynamicBackground):
    def __init__(self, model: ModelWithDecisionFunction, data, **kwargs):
        super().__init__(model, None)

        self.data = data
        self.kwargs = kwargs

    @property
    def preds(self):
        if self._data is None:
            self._raise_data_error()
        return self._preds

    @property
    def weights(self):
        if self._data is None:
            self._raise_data_error()
        return self._weights

    @BaseSupportsDynamicBackground.data.setter
    def data(self, data):
        if data is not None:
            data = self.preprocess(data)
            n, m = data.shape
            data = np.resize(data, (n + 1, m))
            self._data = data
            self._preds = self.model.decision_function(self.data)
            self._weights = np.ones(data.shape[0])

            # Set weight of the quary instance to be equivalent to that of all the others
            self._weights[-1] = self.data.shape[0] - 1
        else:
            self._data = None
            self._preds = None
            self._weights = None

    def fit_regression(self, x):
        ridge = Ridge(**self.kwargs)
        self.data[-1] = x
        self.preds[-1] = self.model.decision_function(np.array([x]))[0]
        ridge.fit(self.data, self.preds, sample_weight=self.weights)
        return ridge.coef_

    def shap_values(self, X):
        X = self.preprocess(X)
        return np.array([self.fit_regression(x) for x in X])
