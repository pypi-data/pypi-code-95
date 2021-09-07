from typing import List
import logging

import numpy as np

from ..tree import TreeExplainer


class SumTreeExplainer(TreeExplainer):
    def __init__(self, model, feature_groups: List[List[int]], *args, **kwargs):
        super().__init__(model, *args, **kwargs)

        self.feature_groups = feature_groups

        self.group_mask = None

    def __initialize_masks(self, X):
        features_in_groups = sum(self.feature_groups, [])
        nb_features = X.shape[1]
        nb_groups = len(self.feature_groups)

        if nb_groups > nb_features:
            logging.error('There are more groups than features.')

        if len(set(features_in_groups)) != len(features_in_groups):
            logging.error('Some features are in multiple groups!')

        if len(set(features_in_groups)) < nb_features:
            logging.error('Not all the features are in groups')

        if any([len(x) == 0 for x in self.feature_groups]):
            logging.error('Some feature groups are empty!')

        mask = np.zeros((nb_groups, nb_features), dtype=bool)
        for i, group in enumerate(self.feature_groups):
            mask[i, group] = True
        self.group_mask = mask

    def shap_values(self, X):

        # Initialize the sum mask
        if self.group_mask is None:
            self.__initialize_masks(X)

        # Compute Shapley values
        values = super().shap_values(X)

        # Sum the values accordingly to the groups
        group_values = np.zeros((values.shape[0], len(self.feature_groups)))
        for i, mask in enumerate(self.group_mask):
            group_values[:, i] = values.sum(axis=1, where=mask)

        return group_values
