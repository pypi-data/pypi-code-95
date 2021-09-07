from unicodedata import normalize
from emutils.geometry import scaled_linspace
import numpy as np
import pandas as pd

from .api import BaseExplainer
from .tree import TreeExplainer


class IntegratedSHAP(BaseExplainer):
    def __init__(self, model, ref_point, scaler, nb_pieces=100):

        self.model = model
        self.scaler = scaler
        self.ref_point = ref_point
        self.n = nb_pieces

    def __explain_piece(self, x, y):
        explainer = TreeExplainer(self.model, data=x.reshape(1, -1), feature_perturbation='interventional')
        return explainer.shap_values(np.array([y]))[0]

    def _integration_points(self, x):
        return scaled_linspace(
            x=self.ref_point,
            y=x,
            num=self.n,
            scaler=self.scaler,
        )

    def __shap_values(self, X):
        for x in X:
            integration_points = self._integration_points(x)
            yield np.array(
                [self.__explain_piece(x=integration_points[i], y=integration_points[i + 1]) for i in range(self.n)]
            ).sum(axis=0)

    def shap_values(self, X):
        return np.array(list(self.__shap_values(X)))
