import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

import numpy as np
import xgboost as xgb
# from xgboost import Booster
from emutils.dsutils import process_data


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class XGBClassifierSKLWrapper:
    """
        Model wrapper that provide the `predict` and `predict_proba` interface
        for compatibility with all methods expecting SKLEAR-like output
    """
    def __init__(self, booster, features, classes=2, ntree_limit=0, threshold=.5):
        self.booster = booster
        self.ntree_limit = ntree_limit
        self.threshold = threshold
        self.features = features

        # scikit-learn compatible attributes
        self.classes_ = np.arange(classes) if isinstance(classes, int) else np.array(classes)
        self.n_classes_ = classes if isinstance(classes, int) else len(classes)
        self.n_features_ = features if isinstance(features, int) else len(features)
        self.n_outputs_ = 1

    def predict(self, X, *args, **kwargs):
        """
            Returns:
                [np.ndarray] : shape = (n_samples)
                The prediction (0 or 1), it returns 1 iff `probability of class 1 > self.threshold`
        """
        X = process_data(X, ret_type='np', names=self.features)
        return (self.booster.predict(xgb.DMatrix(X), ntree_limit=self.ntree_limit) > self.threshold) * 1

    def predict_margin(self, X, *args, **kwargs):
        X = process_data(X, ret_type='np', names=self.features)
        return self.booster.predict(xgb.DMatrix(X), ntree_limit=self.ntree_limit, output_margin=True)

    def decision_function(self, *args, **kwargs):
        return self.predict_margin(*args, **kwargs)

    def predict_probs(self, X, *args, **kwargs):
        """
            Returns:
                [np.ndarray] : shape = (n_samples)
                It is the probability of class 1
        """
        X = process_data(X, ret_type='np', names=self.features)
        return self.booster.predict(xgb.DMatrix(X), ntree_limit=self.ntree_limit)

    def predict_proba(self, X, *args, **kwargs):
        """
            Returns:
                [np.ndarray] : shape = (n_samples, 2)
                [:, 0] is the probability of class 0
                [:, 1] is the probability of class 1
        """
        ps = self.predict_probs(X, *args, **kwargs).reshape(-1, 1)
        return np.hstack([1 - ps, ps])

    def margin_to_probs(self, margin, *args, **kwars):
        return sigmoid(margin)

    def margin_to_prob(self, margin, *args, **kwars):
        return sigmoid(margin)

    def prob_to_predict(self, prob):
        assert isinstance(prob, np.number)
        return 1 * (prob > self.threshold)

    def probs_to_predict(self, probs):
        assert len(probs.shape) == 1
        return 1 * (probs > self.threshold)

    def proba_to_predict(self, proba):
        assert len(proba.shape) == 2
        return 1 * (proba[:, 1] > self.threshold)

    def get_booster(self):
        return self.booster