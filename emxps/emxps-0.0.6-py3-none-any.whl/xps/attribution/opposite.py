from abc import ABCMeta
import numpy as np

from .api import BaseExplainer
from .tree import TreeExplainer

__all__ = ['ModelOppositeExplainer', 'DataOppositeExplainer', 'DifferentLabelExplainer', 'DifferentPredictionExplainer']


class OppositeExplainer(BaseExplainer, metaclass=ABCMeta):
    def __init__(self, model):
        self.model = model

    def get_background_data(self, X):
        X = self.preprocess(X)
        pred = self.model.predict(X)
        return [self.explainers[int(1 - p)].data for p in pred]

    def shap_values(self, X):
        X = self.preprocess(X)
        pred = self.model.predict(X)
        return np.concatenate(
            [self.explainers[int(1 - p)].shap_values(x.reshape(1, -1)) for x, p in zip(X, pred)], axis=0
        )


class ModelOppositeExplainer(OppositeExplainer):
    """
    The samples that are used as reference dataset of SHAP are samples of `data` that
    are predicted as being of the opposite class
    """
    def __init__(self, model, data, **kwargs):
        super().__init__(model)
        data = self.preprocess(data)
        self.explainers = {
            j: TreeExplainer(
                self.model,
                data=data[self.model.predict(data) == j],
                feature_perturbation='interventional',
                **kwargs,
            )
            for j in [0, 1]
        }


class DataOppositeExplainer(OppositeExplainer):
    """
    The samples that are used as reference dataset of SHAP are samples of `data` that
    are predicted as being of the opposite class
    """
    def __init__(self, model, X, y, **kwargs):
        super().__init__(model)
        X = self.preprocess(X)
        y = np.asarray(y).flatten()
        self.explainers = {
            j: TreeExplainer(
                self.model,
                data=X[y == j],
                feature_perturbation='interventional',
                **kwargs,
            )
            for j in [0, 1]
        }


# TODO: Make this standard names
DifferentLabelExplainer = DataOppositeExplainer
DifferentPredictionExplainer = ModelOppositeExplainer