from art import estimators
import numpy as np
from trojai.estimators.ClassifierBase import TrojClassifier
try:
    import tensorflow.compat.v1 as tf
except:
    import tensorflow as tf
"""
Inherits from the troj base class and the ART tensorflow v1 classifier for tf1 support
Also implements our ComputeLoss function which will be called by each classifier, should implement as abstract method in base class
"""


class TrojTF1Classifier(estimators.classification.TensorFlowClassifier, TrojClassifier):
    from art.estimators.classification import TensorFlowClassifier

    """
    Compute loss computes the loss over a batch of target samples
    :param x: inputs
    :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
    the first dimension because of art bug.
    :param return_preds: bool to return model predictions with loss
    :return: Loss values and optionally predictions
    """

    def ComputeLoss(self, x, y, return_preds=True):
        try:
            import tensorflow.compat.v1 as tf
        except:
            import tensorflow as tf
        from numpy import array

        # this has got to be wrong
        shape = (y.size, self.nb_classes)
        one_hot = np.zeros(shape)
        losses = np.array([])
        for sample in x:
            image = np.expand_dims(sample, axis=0)
            rows = np.arange(y.size)
            # print(rows)
            one_hot[rows, y] = 1.0
            # print(one_hot)
            label = np.expand_dims(one_hot[0], axis=0)
            loss_val = self.compute_loss(x, one_hot)
            losses = np.append(losses, loss_val)

        if return_preds:
            preds = self.predict(x)
            return losses, preds
        else:
            return loss_val.numpy()