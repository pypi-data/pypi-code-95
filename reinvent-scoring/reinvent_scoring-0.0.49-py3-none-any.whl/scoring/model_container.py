from typing import List

import numpy as np

from reinvent_scoring.chemistry.descriptors import Descriptors


class ModelContainer:
    def __init__(self, activity_model, model_type: str, specific_parameters: {}):
        """
        :type activity_model: scikit-learn type of model object
        :type model_type: can be "classification" or "regression"
        """
        self._activity_model = activity_model
        self._model_type = model_type
        self._CONTAINER_VERSION = "2.1"
        self._molecules_to_descriptors = self._load_descriptor(specific_parameters)

    def predict_from_mols(self, molecules: List, parameters: dict):
        """
        :return: activity predictions and a set of valid indices indicating which are the valid smiles
        :param molecules: list of RDKit molecule objects
        :type parameters: this is a dictionary object that contains the boundary constants for
        scaling continuous values via sigmoid function. The expected keys are: "low" "high" and "k"
        to calculate the sigmoid scaling key "sigmoid" should be set to True
        """

        if len(molecules) == 0:
            return np.empty([])
        fps = self._molecules_to_descriptors(molecules, parameters)
        activity = self.predict_from_fingerprints(fps)
        return activity

    def predict_from_fingerprints(self, fps):
        if self._model_type == "regression":
            activity = self._activity_model.predict(fps)
        else:
            predictions = self._activity_model.predict_proba(fps)
            activity = predictions[:, 1]

        return activity

    def _load_descriptor(self, parameters: {}):
        descriptors = Descriptors()
        descriptor = descriptors.load_descriptor(parameters)
        return descriptor
