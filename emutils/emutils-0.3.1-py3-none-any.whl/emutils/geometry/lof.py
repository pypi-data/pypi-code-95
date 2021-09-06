import time
import logging

import numpy as np

import sklearn

from emutils.utils import np_sample
from emutils.dsutils import process_data, sample_data
from .metrics import get_metric_name, get_metric_params


class NormalizedLOF:
    def __init__(
        self,
        X,
        K,
        metric,
        normalizer,
        method,
        random_state,
        sample_size,
        # leaf_size,
        # n_jobs,
        **kwargs,
    ):
        start_t = time.time()

        # Pre-process metric
        metric = get_metric_name(metric)
        metric_params = get_metric_params(metric, **kwargs)

        # Normalize data
        X_train_ = normalizer.transform(sample_data(X, n=sample_size, random_state=random_state), method=method)

        # Create the LOF
        lof = sklearn.neighbors.LocalOutlierFactor(
            n_neighbors=K,
            algorithm='auto',
            metric=metric,
            novelty=True,
            metric_params=metric_params,
            **kwargs,
        )

        # Fit the LOF model
        logging.info('Fitting sklearn-LOF...')
        lof.fit(X_train_)
        logging.info(f'Fitting the LOF model took {time.time()-start_t} seconds.')

        # Attributes
        self.method = method
        self.normalizer = normalizer
        self.lof = lof

    # LOF
    def local_outlier_factor(self, X):
        X__ = self.normalizer.transform(X, method=self.method)
        return self.lof.decision_function(X__)

    # K-NN Distances
    def kneighbors_distance(self, X, aggregate=np.mean):
        X__ = self.normalizer.transform(X, method=self.method)
        distances = self.lof.kneighbors(X__)[0]
        if aggregate is not None:
            return aggregate(distances, axis=1)
        else:
            return distances
