import numpy as np
from tqdm import tqdm

from ...api import XGBWrapping
from ..api import BaseDiverseCounterfactualMethod
from ....monotonefeature import Feature
from ....decompose import get_feature_splits, get_graphs
from .utils import Tree


class FeatureTweaking:
    def __init__(self, model, trees, monotonic=False):
        self.trees = trees
        self.model = model
        self.monotonic = monotonic

    def __tweaks(self, x, pred):
        """
            Returns all paths that if taken could move the prediction outcome toward a change
            TODO: non-binary
        """
        return sum([T.relevant_tweaks(x, pred, monotonic=self.monotonic) for T in self.trees], [])

    def tweaks(self, x):
        # Predict probability
        margin = self.model.predict_margin(x.reshape(1, -1))[0]
        prob = self.model.margin_to_prob(margin)
        pred = self.model.prob_to_predict(prob)

        # Get all paths that can be tweaked to move the prediction
        tweaks = self.__tweaks(x, pred)

        # Compute tweaks effects
        X_primes = np.array([tweak.x_prime for tweak in tweaks])
        margin_primes = self.model.predict_margin(X_primes)
        prob_primes = self.model.margin_to_probs(margin_primes)
        pred_primes = self.model.probs_to_predict(prob_primes)

        # Set attributes
        for tweak, margin_prime, prob_prime, pred_prime in zip(tweaks, margin_primes, prob_primes, pred_primes):
            tweak.set(
                delta=(prob_prime - prob),
                margin_delta=(margin_prime - margin),
                effective=(pred != pred_prime),
            )
        return tweaks


class Tolomei(BaseDiverseCounterfactualMethod):
    def __init__(
        self,
        model,
        feature_names,
        feature_trends=None,
        monotonic=True,
    ):
        super().__init__(model)

        # Check if it is a XGB model
        if 'booster' in dir(model):
            # Check if it is a Wrapper
            if isinstance(model, XGBWrapping):
                booster = model.get_booster()
            else:
                raise ValueError('XGB models must be wrapped with the sklearn-compatible wrapper.')
        else:
            raise ('Tolomei\'s method supports only XGB models')

        nodes = booster.trees_to_dataframe()
        splits = get_feature_splits(nodes, features=feature_names)

        features_objs = [
            Feature(
                idx=f,
                name=name,
                trend=trend,
                splits=split,
            ) for f, (trend, name, split) in enumerate(zip(feature_trends, feature_names, splits))
        ]

        # Trees graphs
        nodes = booster.trees_to_dataframe()
        _, Ts = get_graphs(nodes, feature_names)
        trees = [Tree(T, features_objs) for T in Ts]

        self.ft = FeatureTweaking(
            model=model,
            trees=trees,
            monotonic=monotonic,
        )

    def get_diverse_counterfactuals(self, X):
        X = self.preprocess(X)

        X_counter = []
        for x in tqdm(X, desc='Feature Tweaking'):
            tweaks = self.ft.tweaks(x)
            X_C = np.array([t.x_prime for t in tweaks if t.effective])
            X_counter.append(X_C)

        X_counter = self.diverse_postprocess(X, X_counter)
        return X_counter
