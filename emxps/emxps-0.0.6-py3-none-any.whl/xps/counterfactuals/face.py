from typing import Union, Iterable
import logging
import warnings
from collections import defaultdict
import numpy as np

from scipy.sparse.csgraph import dijkstra
from scipy.sparse import SparseEfficiencyWarning
from sklearn.neighbors import NearestNeighbors

from emutils.geometry.metrics import get_metric_name_and_params
from emutils.utils import np_sample

from .api import BaseDiverseCounterfactualMethod

__all__ = ['FACE']


class FACE(BaseDiverseCounterfactualMethod):
    def __init__(
        self,
        model,
        data,
        scaler=None,
        nb_diverse_counterfactuals=10,
        mode: str = "knn",
        n_neighbors=50,
        radius=None,
        distance=None,
        max_samples=None,
        random_state=2020,
        **distance_params
        # immutables: Iterable[int] = [],
    ) -> None:

        super().__init__(model, scaler=scaler)

        self.mode = mode
        # self.immutables = immutables

        # Setup params for distance
        if distance is None:
            self.neighbors_mode = 'connectivity'
            self.metric, self.metric_params = None, None
        else:
            self.neighbors_mode = 'distance'
            self.metric, self.metric_params = get_metric_name_and_params(distance, **distance_params)

        # Data
        self.data = self.preprocess(data)

        # Sample data
        if max_samples is not None:
            self.data = np_sample(self.data, n=max_samples, safe=True, seed=random_state)

        self.preds = self.model.predict(self.data)
        self.preds_indices = self._compute_preds_indices()

        if isinstance(n_neighbors, int) and n_neighbors >= 1:
            self.n_neighbors = min(len(data), n_neighbors)
        elif isinstance(n_neighbors, float) and n_neighbors <= 1.0 and n_neighbors > 0.0:
            self.n_neighbors = int(max(1, round(len(data) * n_neighbors)))
        else:
            raise ValueError(
                'Invalid n_neighbors, it must be the number of neighbors (int) or the fraction of the dataset (float)'
            )

        self.radius = radius

        if isinstance(nb_diverse_counterfactuals, int) and nb_diverse_counterfactuals >= 1:
            self.nb_diverse_counterfactuals = min(len(data), nb_diverse_counterfactuals)
        elif isinstance(
            nb_diverse_counterfactuals, float
        ) and nb_diverse_counterfactuals <= 1.0 and nb_diverse_counterfactuals > 0.0:
            self.nb_diverse_counterfactuals = int(max(1, round(len(data) * nb_diverse_counterfactuals)))
        else:
            raise ValueError(
                'Invalid nb_diverse_counterfactuals, it must be a number (int) or a fraction of the dataset (float)'
            )

        # Take long, will be computed on the first call
        self.adj_mat = None
        self.nn = None

    def _build_graph(self):
        logging.info('Building graph for FACE...')

        nn = NearestNeighbors(
            radius=self.radius,
            metric=self.metric,
            p=self.metric_params['p'] if 'p' in self.metric_params else 2,
            metric_params=self.metric_params,
        ).fit(self.scale(self.data))

        # Use SKL to compute the sparse adjecency matrix
        if self.mode == 'knn':
            adj_mat = nn.kneighbors_graph(
                X=nn._fit_X,
                n_neighbors=self.n_neighbors,
                mode=self.neighbors_mode,
            )
        elif self.mode == 'epsilon':
            adj_mat = nn.radius_neighbors_graph(
                X=nn._fit_X,
                radius=self.radius,
                mode=self.neighbors_mode,
            )
        else:
            raise ValueError("Invalid mode.")

        # Add one columns and row for the query point to the adjecency matrix
        adj_mat.resize((adj_mat.shape[0] + 1, adj_mat.shape[1] + 1))

        logging.info('FACE graph built.')

        self.nn = nn
        self.adj_mat = adj_mat

    def _update_graph(self, x):

        # Compute the adjecency vector of x wrt. all the other samples
        if self.mode == 'knn':
            adj_vector = self.nn.kneighbors_graph(
                X=self.scale(np.array([x])),
                n_neighbors=self.n_neighbors,
                mode=self.neighbors_mode,
            )[0]
        elif self.mode == 'epsilon':
            adj_vector = self.nn.radius_neighbors_graph(
                X=self.scale(np.array([x])),
                radius=self.radius,
                mode=self.neighbors_mode,
            )[0]
        else:
            raise ValueError("Invalid mode.")

        with warnings.catch_warnings():
            # Suppress warning of efficiency
            # We don't care if for this (columns) operation lil is more efficient.
            # dijkstra needs a csr matrix and converting back and forth is more expensive
            warnings.simplefilter('ignore', SparseEfficiencyWarning)

            # Resize array -> Column vector and distance to itself cell added
            adj_vector.resize((1, adj_vector.shape[1] + 1))

            # Explicitly set connectivity/distance to itself to zero
            adj_vector[0, -1] = 0

            # Update adjacency matrix
            self.adj_mat[-1] = adj_vector
            self.adj_mat[:, -1] = adj_vector.reshape(-1, 1)

    def _compute_preds_indices(self):
        # By default the candidates are all
        indices = defaultdict(lambda: np.array([]))

        for class_index in np.unique(self.preds):
            # NOTE: We are checking only for a change in the prediction
            # (not for density)
            indices[class_index] = np.argwhere(self.preds == class_index).flatten()
        return indices

    def _get_point_counterfactuals(self, x, n=1):
        # Update the graph
        self._update_graph(x)

        # Compute the distance
        distances = dijkstra(self.adj_mat, directed=False, indices=-1)

        # Filter only points with different prediction
        pred = self.model.predict(np.array([x]))[0]
        distances[self.preds_indices[pred]] = np.inf

        # Select the closest n points
        # 1:    -- We ignore the closest because it's the point itself
        # :n+1  -- We take the next n closest
        closest_indices = np.argsort(distances)[1:n + 1]

        # Return the closest
        return self.data[closest_indices]

    def _get_counterfactuals(self, X, diverse=False):
        # Pre-compute the adjacency matrix
        if self.adj_mat is None:
            self._build_graph()

        # Pre-process the data (to NumPy)
        X = self.preprocess(X)

        # Compute counterfactual
        if diverse:
            X_counter = [self._get_point_counterfactuals(x, n=self.nb_diverse_counterfactuals) for x in X]
        else:
            X_counter = np.array([self._get_point_counterfactuals(x)[0] for x in X])

        return X_counter

    def get_counterfactuals(self, X):
        return self.postprocess(X, self._get_counterfactuals(X, diverse=False))

    def get_diverse_counterfactuals(self, X):
        return self.diverse_postprocess(X, self._get_counterfactuals(X, diverse=True))
