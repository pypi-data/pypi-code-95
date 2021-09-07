import numpy as np
import pytest

from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics
from azureml.automl.core.shared import constants


class TestTextClassificationUtils:
    """Tests for utility functions for multi-class text classification."""
    @pytest.mark.parametrize('class_labels, train_labels',
                             [pytest.param(np.array(['ABC', 'DEF', 'XYZ']), np.array(['ABC', 'DEF'])),
                              pytest.param(np.array(['ABC', 'DEF', 'XYZ']), np.array(['ABC', 'DEF', 'XYZ']))])
    def test_compute_metrics(self, class_labels, train_labels):
        predictions = np.random.rand(5, len(train_labels))
        y_val = np.random.choice(class_labels, size=5)
        results = compute_metrics(y_val, predictions, class_labels, train_labels)
        metrics_names = list(constants.Metric.CLASSIFICATION_SET)
        assert all(key in metrics_names for key in results)
