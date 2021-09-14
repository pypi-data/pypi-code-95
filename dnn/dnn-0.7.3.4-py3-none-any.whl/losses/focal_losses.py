"""
https://github.com/umbertogriffo/focal-loss-keras/blob/master/src/loss_function/losses.py
Define our custom loss function.
"""
from tensorflow.keras import backend as K
import tensorflow as tf
import numpy as np

class FocalLoss:
    __name__ = 'FocalLoss'
    def __init__(self, gamma = 2, alpha = 0.25):
        self._gamma = gamma
        self._alpha = alpha

    def __call__ (self, y_true, y_pred):
        return self.compute_loss (y_true, y_pred)

    def compute_loss (self, y_true, y_pred):
        cross_entropy_loss = K.binary_crossentropy (y_true, y_pred, from_logits = False)
        p_t = ((y_true * y_pred) +
               ((1 - y_true) * (1 - y_pred)))
        modulating_factor = 1.0
        if self._gamma:
            modulating_factor = tf.pow(1.0 - p_t, self._gamma)
        alpha_weight_factor = 1.0
        if self._alpha is not None:
            alpha_weight_factor = (y_true * self._alpha +
                                   (1 - y_true) * (1 - self._alpha))
        focal_cross_entropy_loss = (modulating_factor * alpha_weight_factor *
                                    cross_entropy_loss)
        return K.mean (focal_cross_entropy_loss, axis=-1)


def binary_focal_loss (alpha=.25, gamma=2.):
    def binary_focal_loss_fixed (y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        # Define epsilon so that the back-propagation will not result in NaN for 0 divisor case
        epsilon = K.epsilon()
        # Add the epsilon to prediction value
        # y_pred = y_pred + epsilon
        # Clip the prediciton value
        y_pred = K.clip(y_pred, epsilon, 1.0 - epsilon)
        # Calculate p_t
        p_t = tf.where(K.equal(y_true, 1), y_pred, 1 - y_pred)
        # Calculate alpha_t
        alpha_factor = K.ones_like(y_true) * alpha
        alpha_t = tf.where(K.equal(y_true, 1), alpha_factor, 1 - alpha_factor)
        # Calculate cross entropy
        cross_entropy = -K.log(p_t)
        weight = alpha_t * K.pow((1 - p_t), gamma)
        # Calculate focal loss
        loss = weight * cross_entropy
        # Sum the losses in mini_batch
        loss = K.mean(K.sum(loss, axis=1))
        return loss
    return binary_focal_loss_fixed

def categorical_focal_loss (alpha = 0.25, gamma=2.):
    if isinstance (alpha, dict):
        # {class_index: weight}
        alpha = [ w for i, w in sorted (alpha.items (), key = lambda x: x [1]) ]
    alpha = np.array(alpha, dtype=np.float32)
    def categorical_focal_loss_fixed (y_true, y_pred):
        # Clip the prediction value to prevent NaN's and Inf's
        epsilon = K.epsilon()
        y_pred = K.clip(y_pred, epsilon, 1. - epsilon)

        # Calculate Cross Entropy
        cross_entropy = -y_true * K.log(y_pred)

        # Calculate Focal Loss
        loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy

        # Compute mean loss in mini_batch
        return K.mean(K.sum(loss, axis=-1))
    return categorical_focal_loss_fixed
