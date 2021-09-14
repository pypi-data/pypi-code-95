from tensorflow.keras import backend as K
import tensorflow as tf
from sklearn.metrics import confusion_matrix as confusion_matrix_
import numpy as np


def recall (y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision (y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def _f1_score (true, pred):
    ground_positives = K.sum(true, axis=0)       # = TP + FN
    pred_positives = K.sum(pred, axis=0)         # = TP + FP
    true_positives = K.sum(true * pred, axis=0)  # = TP
    precision = (true_positives + K.epsilon()) / (pred_positives + K.epsilon())
    recall = (true_positives + K.epsilon()) / (ground_positives + K.epsilon())
    return 2 * (precision * recall) / (precision + recall + K.epsilon())

def f1_weighted (true, pred):
    score = _f1_score (true, pred)
    ground_positives = K.sum(true, axis=0)
    weighted_f1 = score * (ground_positives / K.sum(ground_positives))
    return K.sum(weighted_f1)

def f1_macro (true, pred):
    return K.mean (_f1_score (true, pred))

def F1 (mode):
    assert mode in ('weighted', 'macro')
    def batchf1 (true, pred):
        return f1_weighted (true, pred) if mode == 'weighted' else f1_macro (true, pred)
    return batchf1

def confusion_matrix (y_true, y_pred):
    return confusion_matrix_ (y_true, y_pred)

