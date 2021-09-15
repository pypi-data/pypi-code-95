from art import estimators
import tensorflow as tf
import numpy as np
from trojai.estimators.ClassifierBase import TrojClassifier

"""
Inherits from the troj base class and the ART tensorflow v2 classifier for tf2 support
Also implements our ComputeLoss function which will be called by each classifier, should implement as abstract method in base class
"""


class TrojKerasClassifier(estimators.classification.KerasClassifier, TrojClassifier):
    import tensorflow as tf

    tf.compat.v1.disable_eager_execution()

    """
    Compute loss computes the loss over a batch of target samples

    :param x: inputs
    :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
    the first dimension because of art bug.
    :param return_preds: bool to return model predictions with loss
    :param reduction: changes the reduction of the loss function to none 
    :return: Loss values and optionally predictions
    """

    def ComputeLoss(
        self, x, y, return_preds=True, reduction=tf.keras.losses.Reduction.NONE
    ):
        # import tensorflow.compat.v1 as tf
        import tensorflow as tf

        old_reduction = self.model.loss_functions[0]._get_reduction()
        self.model.loss_functions[0].reduction = reduction
        preds = self.predict(x)
        # hard_labels = np.argmax(preds, axis=1)
        # hard_labels_dtype = 'float32'
        # y = y.astype(hard_labels_dtype)
        loss_val = self.model.loss_functions[0](y, preds)
        self._loss.reduction = old_reduction
        # tf.compat.v1.enable_eager_execution()
        if return_preds:

            return loss_val.eval(session=tf.compat.v1.Session()), preds
        else:
            return loss_val.numpy()