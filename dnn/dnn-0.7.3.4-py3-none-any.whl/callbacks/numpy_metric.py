from tensorflow.keras.callbacks import Callback
from rs4.termcolor import tc, stty_size
from tensorflow.python.keras import backend as K
from . import base
import numpy as np
from sklearn.metrics import f1_score, confusion_matrix, roc_auc_score, recall_score, precision_score
from .confusion_matrix import calc_metrics

# numpy metrics ---------------------------------
def F1 (mode = 'weighted'):
    def f1_weighted (y_true, y_pred, logs = None, name = None):
        logs = logs or {}
        labels = np.argmax (y_true, axis = 1)
        metrics = calc_metrics (labels, np.argmax (y_pred, axis = 1), average = mode, y_score = y_pred)
        name = name and ('_' + name) or ''
        logs ['val{}_f1'.format (name)] = metrics ['f1']
        logs ['val{}_auc'.format (name)] = metrics ['auc']
        # logs ['val{}_acc'.format (name)] = metrics ['acc']
        # logs ['val{}_prc'.format (name)] = metrics ['prc']
        # logs ['val{}_rcl'.format (name)] = metrics ['rcl']
        return '' # return displayable message
    return f1_weighted


class NumpyMetricCallback (base.ValiadtionSet, Callback):
    def __init__(self, func, validation_data, validation_mode = 'A', average = 'weighted'):
        Callback.__init__(self)
        base.ValiadtionSet.__init__ (self, validation_data)
        self.func = F1 (average) if func == 'f1' else func
        self.validation_mode = validation_mode
        self.info = None

    def get_info (self):
        return self.info

    def on_epoch_end (self, epoch, logs):
        logs = logs or {}
        self.make_predictions ()
        if self.validation_mode == 'B' or not isinstance (self.ys, tuple):
            self.info = self.func (self.ys, self.logits, logs)
        else:
            self.info = []
            for idx in range (len (self.ys)):
                name = self.model.outputs [idx].name.split ("/")[0]
                self.info.append (self.func (self.ys [idx], self.logits [idx], logs, name))
            self.info = '\n'.join (self.info)
