# Keras compatible losses

from . import focal_losses
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.python.keras.losses import LossFunctionWrapper

def weightedcrossentropy (beta = 10):
    def convert_to_logits(y_pred):
        y_pred = tf.clip_by_value(y_pred, tf.keras.backend.epsilon(), 1 - tf.keras.backend.epsilon())
        return tf.math.log(y_pred / (1 - y_pred))

    def loss(y_true, y_pred):
        y_pred = convert_to_logits(y_pred)
        loss = tf.nn.weighted_cross_entropy_with_logits(logits=y_pred, labels=y_true, pos_weight=beta)
        return tf.reduce_mean(loss)
    return loss