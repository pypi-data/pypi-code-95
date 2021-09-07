from abc import ABC, abstractclassmethod
import numpy as np

from ..api import Model
from .api import BaseDiverseCounterfactualMethod

__all__ = ['DifferentLabelCounterfactuals', 'DifferentPredictionCounterfactuals']


class BaseOppositeCounterfactuals(BaseDiverseCounterfactualMethod):
    def __init__(self, model, max_samples=None, random_state=None):
        super().__init__(model)

        self.random_state = random_state
        self.max_samples = max_samples

    @property
    def data(self):
        return self._data

    def _save_data(self, data):
        data = data.copy()
        data = self.sample(data, self.max_samples)
        data.flags.writeable = False
        return data

    def _set_data(self, X, y):
        self._data = X
        self._data_per_class = {j: self._save_data(X[y != j]) for j in np.unique(y)}

    def get_diverse_counterfactuals(self, X):
        X = self.preprocess(X)
        y = self.model.predict(X)
        return [self._data_per_class[j] for j in y]


class ModelOppositeCounterfactuals(BaseOppositeCounterfactuals):
    def __init__(self, model: Model, data, **kwargs):
        super().__init__(model, **kwargs)

        # Based on the prediction
        data = self.preprocess(data)
        self._set_data(data, self.model.predict(data))


class DataOppositeCounterfactuals(BaseOppositeCounterfactuals):
    def __init__(self, model, X, y, **kwargs):
        super().__init__(model, **kwargs)

        # Based on the label
        X = self.preprocess(X)
        self._set_data(X, y)


# Aliases
DifferentPredictionCounterfactuals = ModelOppositeCounterfactuals
DifferentLabelCounterfactuals = DataOppositeCounterfactuals
