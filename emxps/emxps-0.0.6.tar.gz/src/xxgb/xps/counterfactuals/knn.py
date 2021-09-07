from typing import Union

import numpy as np
from sklearn.neighbors import NearestNeighbors
from emutils.utils import keydefaultdict

from .api import BaseDiverseCounterfactualMethod

from emutils.geometry.metrics import get_metric_name_and_params

__all__ = ['KNNCounterfactuals']


class KNNCounterfactuals(BaseDiverseCounterfactualMethod):
    def __init__(
        self,
        model,
        scaler,
        X,
        n_neighbors: Union[int, float] = 5,
        distance=None,
        verbose=0,
        **distance_params,
    ):
        """
            X : The reference dataset for SHAP
            model : sklearn wrapper with .booster for the booster
            normalize_lambda : The function to be used to normalize data
            feature_names : list with the feature names
            pred : pred (i.e., class) to explain, e.g. 0, 1, etc.
        """

        super().__init__(model, scaler)

        self.__metric, self.__metric_params = get_metric_name_and_params(distance, **distance_params)
        self.__n_neighbors = n_neighbors

        self.data = X
        self.verbose = verbose

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._raw_data = self.preprocess(data)
        self._preds = self.model.predict(data)

        # TODO: Make it more general
        # Here we are making a dirty assumption that the we are not interested in the most frequent class
        # -> The max nb of neighbouts will be the one of the least ccuring class
        # (True in most dataset btw)
        _, nb_uniques = np.unique(self._preds, return_counts=True)
        max_nb_neighbors = np.min(nb_uniques)
        if isinstance(self.__n_neighbors, int) and self.__n_neighbors >= 1:
            self._n_neighbors = min(self.__n_neighbors, max_nb_neighbors)
        elif isinstance(self.__n_neighbors, float) and self.__n_neighbors <= 1.0 and self.__n_neighbors > 0.0:
            self._n_neighbors = int(max(1, round(max_nb_neighbors * self.__n_neighbors)))
        else:
            raise ValueError(
                'Invalid n_neighbors, it must be the number of neighbors (int) or the fraction of the dataset (float)'
            )

        # We will be searching neighbors of a different class
        self._data = keydefaultdict(lambda pred: self._raw_data[self._preds != pred])

        self._nn = keydefaultdict(
            lambda pred: NearestNeighbors(
                n_neighbors=self._n_neighbors,
                metric=self.__metric,
                p=self.__metric_params['p'] if 'p' in self.__metric_params else 2,
                metric_params=self.__metric_params,
            ).fit(self.scale(self._data[pred]))
        )

    def get_counterfactuals(self, X):
        # Pre-process
        X = self.preprocess(X)

        preds = self.model.predict(X)
        preds_indices = {pred: np.argwhere(preds == pred).flatten() for pred in np.unique(preds)}

        X_counter = np.zeros_like(X)

        for pred, indices in preds_indices.items():
            _, neighbors_indices = self._nn[pred].kneighbors(self.scale(X), n_neighbors=1)
            X_counter[indices] = self._data[pred][neighbors_indices.flatten()]

        # Post-process
        X_counter = self.postprocess(X_counter)

        return X_counter

    def get_diverse_counterfactuals(self, X):
        # Pre-process
        X = self.preprocess(X)

        preds = self.model.predict(X)
        preds_indices = {pred: np.argwhere(preds == pred).flatten() for pred in np.unique(preds)}

        X_counter = np.zeros((X.shape[0], self._n_neighbors, X.shape[1]))

        for pred, indices in preds_indices.items():
            _, neighbors_indices = self._nn[pred].kneighbors(self.scale(X[indices]), n_neighbors=None)
            X_counter[indices] = self._data[pred][neighbors_indices.flatten()].reshape(
                len(indices), self._n_neighbors, -1
            )

        # Post-process
        # X_counter = X_counter.reshape(X.shape[0], self._n_neighbors, X.shape[1])
        X_counter = self.diverse_postprocess(X, X_counter)

        return X_counter
