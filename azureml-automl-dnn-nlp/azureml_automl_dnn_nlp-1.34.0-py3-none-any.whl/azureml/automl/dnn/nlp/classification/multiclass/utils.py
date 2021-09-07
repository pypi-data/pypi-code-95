# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions for multi-class classification."""

import numpy as np
import scipy
from typing import Any, Dict, Union
from azureml.automl.runtime._ml_engine import evaluate_classifier
from azureml.automl.core.shared import constants


def compute_metrics(y_val: np.ndarray, predictions: np.ndarray, class_labels: np.ndarray,
                    train_labels: np.ndarray) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Function to compute metrics like accuracy and auc-weighted

    :param predictions: Predictions on the validation/test dataset used for computing metrics.
    :return: A dictionary mapping metric name to metric score.
    """
    probas = scipy.special.softmax(predictions, axis=1)
    metrics_names = list(constants.Metric.CLASSIFICATION_SET)
    return evaluate_classifier(y_val, probas, metrics_names, class_labels, train_labels)
