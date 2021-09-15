from art import estimators
import torch
from trojai.estimators.ClassifierBase import TrojClassifier

"""
Inherits from the troj base class and the ART Pytorch classifier for Pytorch support
Also implements our ComputeLoss function which will be called by each classifier, should implement as abstract method in base class
"""


class TrojPytorchClassifier(
    estimators.classification.PyTorchClassifier, TrojClassifier
):
    """
    Compute loss computes the loss over a batch of target samples

    :param x: inputs
    :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
    the first dimension because of art bug.
    :param return_preds: bool to return model predictions with loss
    :return: Loss values and optionally predictions
    """

    def ComputeLoss(self, x, y, return_preds=True, reduction="none"):

        old_reduction = self._loss.reduction
        self._loss.reduction = reduction
        preds = torch.tensor(self.predict(x))
        y = torch.tensor(y)
        loss_val = self._loss(preds, y)
        self._loss.reduction = old_reduction
        if return_preds:
            return loss_val.numpy(), preds.numpy()
        else:
            return loss_val.numpy()
