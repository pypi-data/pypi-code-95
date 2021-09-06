from abc import abstractmethod, ABC
import numpy as np

from .api import BaseExplainer, ExplainerSupportsDynamicBackground
from ..counterfactuals import CounterfactualMethod
from ..counterfactuals import DiverseCounterfactualMethod

__all__ = [
    'CFExplainer',
    'CFExplainerNoWorse',
    'CFEplainerNoWorseDistribution',
]


class CFExplainer(BaseExplainer):
    def __init__(
        self,
        counterfactual_method: CounterfactualMethod,
        explainer: ExplainerSupportsDynamicBackground,
    ):
        super().__init__(counterfactual_method.model)
        self.counterfactual_method = counterfactual_method
        self.explainer = self.last_explainer = explainer

        self.last_X = None

    def get_background_data(self, X):
        X = self.preprocess(X)
        if isinstance(self.counterfactual_method, DiverseCounterfactualMethod):
            return self.counterfactual_method.get_diverse_counterfactuals(X)
        else:
            return np.expand_dims(self.counterfactual_method.get_counterfactuals(X), axis=1)

    @abstractmethod
    def create_explainer(self, X):
        pass

    def shap_values(self, X, log_average=False):
        X = self.preprocess(X)
        res = []
        X_counters = self.get_background_data(X)
        for x, X_counter_ in zip(X, X_counters):
            self.last_X = X_counter_
            if len(X_counter_) > 0:
                self.explainer.data = X_counter_
                res.append(self.explainer.shap_values(x.reshape(1, -1))[0])
            else:
                self.last_explainer = None
                res.append(None)
        if log_average:
            if log_average is True:

                def log_average_(X_C):
                    return np.mean(X_C, axis=0)

                log_average = log_average_
            if isinstance(log_average, dict):
                log_averages_ = {
                    name: np.array(
                        [
                            # Handle empty set of counterfactuals (return NaN)
                            func(X_counter) if len(X_counter) > 0 else np.full(X.shape[1], np.nan)
                            for X_counter in X_counters
                        ]
                    )
                    for name, func in log_average.items()
                }
            else:
                log_averages_ = dict()
                log_averages_['mean'] = np.array([log_average(X_counter) for X_counter in X_counters])

        if log_average:
            return np.array(res), log_averages_
        else:
            return np.array(res)

    def get_last_counterfactuals(self):
        return self.last_X

    def get_last_explainer(self):
        return self.last_explainer


class CFExplainerNoWorse(CFExplainer):
    def __init__(self, *args, feature_trends=None, **kwargs):
        super().__init__(*args, **kwargs)

        if feature_trends is None:
            raise ValueError('feature_trends cannot be None.')

        self.feature_trends = np.array(feature_trends)
        assert ((self.feature_trends == -1).sum() +
                (self.feature_trends == 1).sum()) == len(feature_trends), 'Feature trends must be +1 or -1'

    def __trends_maks(self, X, pred):
        # Trend mask
        mask = (pred * 2 - 1) * np.tile(self.feature_trends, (X.shape[0], 1))
        mask_pos = (mask == 1)
        mask_neg = (mask == -1)
        assert mask_pos.sum() + mask_neg.sum() == mask.shape[0] * mask.shape[1]
        return mask_pos, mask_neg

    def __filter_counters(self, X, x, pred):
        # Get trend mask
        mask_pos, mask_neg = self.__trends_maks(X, pred)

        # Expand x
        x_ = np.tile(x, (X.shape[0], 1))

        # Replace with x_i where:
        # - positive trend (and class 1) AND x'_i is greater than x_i
        # - negative trend (and class 1) AND x'_i is lesser than x_i
        X = np.where(mask_pos & (X > x_), x_, X)
        X = np.where(mask_neg & (X < x_), x_, X)
        return X

    def get_background_data(self, X):
        X = self.preprocess(X)
        X_counters = super().get_background_data(X)
        preds = self.model.predict(X)
        return [self.__filter_counters(X_counter_, x, pred) for x, X_counter_, pred in zip(X, X_counters, preds)]


class CFEplainerNoWorseDistribution(CFExplainerNoWorse):
    def __init__(self, *args, random_state=0, **kwargs):
        super().__init__(*args, **kwargs)

        self.random_state = random_state

    def __filter_counters(self, X, x, pred):
        # Get trend mask
        mask_pos, mask_neg = self.__trends_maks(X, pred)

        # Expand x
        x_ = np.tile(x, (X.shape[0], 1))

        # Create NaNs
        NaN = np.full(X.shape, np.nan)

        # Replace with nan where:
        # - positive trend (and class 1) AND x'_i is greater than x_i
        # - negative trend (and class 1) AND x'_i is lesser than x_i
        X = np.where(mask_pos & (X > x_), NaN, X)
        X = np.where(mask_neg & (X < x_), NaN, X)

        # If all NaN in a feature replace with x_i
        s = X.sum(axis=0)
        for f in range(X.shape[1]):
            if s[f] == X.shape[0]:
                X[:, f] = x[f]

        # Replace NaN with the ones that are no NaN (at random)
        r = np.random.RandomState(self.random_state)
        R_ = np.hstack(
            [r.choice(X[:, f][~np.isnan(X[:, f])], size=X.shape[0], replace=True) for f in range(X.shape[1])]
        )

        X = np.where(np.isnan(X), R_, X)
        X = np.where(np.isnan(X), R_, X)

        return X