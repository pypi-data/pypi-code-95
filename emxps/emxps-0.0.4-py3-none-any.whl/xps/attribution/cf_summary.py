import numpy as np
from emutils.dsutils import process_data
from emutils.geometry import adist

from .api import BaseExplainer
from ..counterfactuals import CounterfactualMethod
from ..counterfactuals import DiverseCounterfactualMethod

# %%


class CFSummarizer(BaseExplainer):
    def __init__(
        self,
        counterfactual_method: CounterfactualMethod,
        aggregation=np.mean,
        scaler=None,
        feature_trends=None,
        binary=False,
    ):
        super().__init__(counterfactual_method.model)
        self.counterfactual_method = counterfactual_method
        self.aggregation = aggregation
        self.scaler = scaler
        self.feature_trends = feature_trends

        self.last_X = None
        self.last_explainer = None

    def get_background_data(self, X):
        if isinstance(self.counterfactual_method, DiverseCounterfactualMethod):
            return self.counterfactual_method.get_diverse_counterfactuals(X)
        else:
            return np.expand_dims(self.counterfactual_method.get_counterfactuals(X), axis=1)

    def shap_values(self, X):
        X = self.preprocess(X)
        res = []
        X_counters = self.get_background_data(X)
        preds = self.model.predict(X)

        assert np.all(preds <= 1)  # Binary

        for x, pred, X_counter_ in zip(X, preds, X_counters):
            if len(X_counter_) < 1:
                # No explanation
                res.append(None)
            else:
                # Scale
                x = self.scale(np.array([x]))[0]
                X_counter_ = self.scale(X_counter_)

                # Measure distance
                X__ = np.tile(x, (len(X_counter_), 1))
                difference = X_counter_ - X__

                # Filter only monotone
                if self.feature_trends is not None:
                    trends__ = np.tile(self.feature_trends, (len(X_counter_), 1))
                    feature_mask = ((pred * 2 - 1) * trends__ * difference) < 0
                    difference = difference * (1 * feature_mask)

                # Take abs
                difference = np.abs(difference)

                # Binary output (proportion)
                difference = (difference > 0)

                phi = self.aggregation(difference, axis=0)
                res.append(phi)

        return np.array(res)

    def get_last_counterfactuals(self):
        return self.last_X

    def get_last_explainer(self):
        return self.last_explainer


# %%
