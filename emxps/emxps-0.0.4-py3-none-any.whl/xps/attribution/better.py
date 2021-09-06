import numpy as np
import logging

from .api import BaseExplainer
from .tree import TreeExplainer


class ModelBetterExplainer(BaseExplainer):
    """
    The samples that are used as reference dataset of SHAP are samples of `data` that have
    better prediction (in terms of probability)
    """
    def __init__(self, model, data, feature_names):
        super().__init__(model)

        self.feature_names = feature_names

        self.last_explainer = None
        self.last_X = None

        self.probs = model.predict_probs(data[feature_names].values)
        self.data = data[feature_names].values[np.argsort(self.probs)]

    def shap_values(self, X):
        ret = []
        # Predict the class
        probs = self.model.predict_probs(X)
        preds = self.model.predict_predict(X)
        for x, p, pr in zip(X, preds, probs):
            # Get as reference only the samples with better prediction
            if p == 0:
                start_index = np.searchsorted(self.probs, pr, side='right')
                ref_data = self.data[start_index:]
            else:
                start_index = np.searchsorted(self.probs, pr, side='left')
                ref_data = self.data[:start_index]
            ref_data = self.last_X = ref_data
            # logging.debug(f'Ref Filter: {ref_data.shape}')
            # Explain
            if len(ref_data) > 0:
                explainer = self.last_explainer = TreeExplainer(
                    self.model,
                    data=ref_data,
                    feature_perturbation='interventional',
                )
                ret.append(explainer.shap_values(x.reshape(1, -1))[0])
            else:
                self.last_explainer = None
                ret.append(None)
        return np.array(ret)


class StricklyMonotononeModelBetterExplainer(BaseExplainer):
    """
        The samples that are used as reference dataset of SHAP are samples of `data` that
        have no feature value that is worse than the explained sample value
        where 'worse' means moving in the opposite direction (than the one necessary to change the predcition)
        with respect to the monotonic trend of the model
    """
    def __init__(self, model, data, feature_names, feature_trends):
        super().__init__(model)

        data = self.preprocess(data)

        self.feature_names = feature_names
        self.feature_trends = feature_trends

        self.last_explainer = None
        self.last_X = None

        self.data = {j: data[model.predict(data) == j] for j in [0, 1]}

    def get_background_data(self, X):
        X = self.preprocess(X)
        pred = self.model.predict(X)
        backgrounds = []
        for x, p in zip(X, pred):
            # Get as reference only the samples with the opposite class
            ref_data = self.data[int(1 - p)]
            # Get only the samples that do not worsen any feature in the wrong direction
            c = np.ones(len(ref_data), dtype=bool)
            for f in range(X.shape[1]):
                t = self.feature_trends[f] * (-1 + 2 * p)
                c = c & (t * ref_data[:, f] <= t * x[f])
            backgrounds.append(ref_data[c])
        return backgrounds

    def shap_values(self, X):
        X = self.preprocess(X)
        ret = []
        Background = self.get_background_data(X)
        for x, ref_data in zip(X, Background):
            self.last_X = ref_data
            # Explain
            if len(ref_data) > 0:
                explainer = self.last_explainer = TreeExplainer(
                    self.model,
                    data=ref_data,
                    feature_perturbation='interventional',
                )
                ret.append(explainer.shap_values(x.reshape(1, -1))[0])
            else:
                self.last_explainer = None
                ret.append(None)
        return np.array(ret)
