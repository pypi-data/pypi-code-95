import tensorflow as tf
from . import confusion_matrix
from . import best_metrics
from . import numpy_metric
import math
import os
import shutil
from rs4 import pathtool
from . import plot_progress, clear_output, base
from importlib import reload
import warnings
import numpy as np
from tensorflow.python.keras import backend
from keras.callbacks import CSVLogger, LambdaCallback
from importlib import reload
from tqdm.keras import TqdmCallback
from tensorflow.keras.callbacks import Callback
import time

def monitor_options (monitor):
    if isinstance (monitor, (list, tuple)):
        monitor, mode = monitor
        if monitor.endswith ('loss'):
            assert mode == 'min', 'val_loss monitoring shoul be min'
    else:
        mode = 'min' if monitor.endswith ('loss') else 'max'
    return monitor, mode


# lr schedule functions --------------------------
def step_decay (initial_lrate, decay_rate, per_epochs):
    def step_decay (epoch):
        lrate = initial_lrate * math.pow (decay_rate, math.floor((1+epoch)/per_epochs))
        return lrate
    return step_decay

def cosine_decay_restarts (initial_lrate, period_epochs, decay_rate_per_period = 1.0, increasing_period = 2.0):
    try:
        fn = tf.keras.optimizers.schedules.CosineDecayRestarts
    except AttributeError:
        fn = tf.keras.experimental.CosineDecayRestarts
    return fn (
        initial_lrate, period_epochs, t_mul = increasing_period, m_mul = decay_rate_per_period, alpha = 0.0
    )

def plateau_decay_hot_start (model, initial_lr, keep = 3, plateau_decay = (1e-4, 0.6, 5)):
    rrp = None
    def fixed (epoch):
        nonlocal rrp
        if epoch < keep:
            return 4e-4
        if epoch == keep:
            rrp = LRPlateauDecay (*plateau_decay)
            rrp.set_model (model)
            rrp._reset()
        rrp.on_epoch_end (epoch)
        return backend.get_value (rrp.model.optimizer.lr)


# callbacks --------------------------------------
class ReduceLROnPlateau (tf.keras.callbacks.ReduceLROnPlateau):
    def __init__ (self, initial_lr, *args, **kargs):
        self._initial_lr = initial_lr
        super ().__init__ (*args, **kargs)

    def on_train_begin (self, logs = None):
        backend.set_value (self.model.optimizer.lr, self._initial_lr)
        return super ().on_train_begin (logs)

def LRPlateauDecay (initial_lr, factor = None, patience = 5, monitor='val_loss', min_lr=1e-7):
    return ReduceLROnPlateau (initial_lr, monitor = monitor, factor = factor or np.sqrt (0.1), patience=patience, min_lr=1e-7)


class TimeLogging (Callback):
    def __init__ (self):
        super ().__init__ ()
        self._train_begin = 0
        self._epoch_begin = 0

    def on_train_begin (self, logs = None):
        self._train_begin = time.time ()

    def on_epoch_begin (self, epoch, logs = None):
        self._epoch_begin = time.time ()

    def on_epoch_end (self, epoch, logs = None):
        logs ['time_epoch'] = (time.time () - self._epoch_begin) / 60
        logs ['time_train'] = (time.time () - self._train_begin) / 60


def tolist (obj):
    if not obj:
        return []
    if isinstance (obj, (list, tuple)):
        return obj
    return [obj]

# compsing -------------------------------------
def compose (
        train_dir, datasets,
        monitor = None, # monitor or (monitor, mode)
        custom_metric = 'f1', # function or custom metric name
        learning_rate = None, # lr scehduler_func or (learing_rate, decay_rate [, decay_patience])
        early_stop = None, # patience or (patience, monitor, mode)
        enable_logging = False, # enable tensor board logging
        reset_train_dir = False,
        plots = ['loss'],
        average = 'weighted',
        decay_rate = None, # for lower version compat, synonym with learning_rate
        custom_validation = 'A' # True/False or mode name: `A` to handle outputs seperately, `B` to handle outputs at once
):
    assert custom_validation in (True, False, 'A', 'B')
    if custom_validation is True:
        custom_validation = 'A'
    reset_train_dir and os.path.isdir (train_dir) and shutil.rmtree (train_dir)

    CHECKPOINT_FORMAT = os.path.join (train_dir, 'checkpoint', '{epoch:04d}.ckpt')
    ASSETS_DIR = os.path.join (train_dir, 'assets')
    LOG_DIR = os.path.join (train_dir, 'log')
    pathtool.mkdir (ASSETS_DIR)

    composed_callbacks, intels = [], []
    composed_callbacks.append (clear_output.ClearOutput ())
    composed_callbacks.append (TimeLogging ())
    if datasets.validset and custom_validation:
        if custom_metric:
            if not isinstance (custom_metric, (list, tuple)):
                custom_metric = [custom_metric]
            for cm in custom_metric:
                custom_metric = numpy_metric.NumpyMetricCallback (cm, datasets.validset, custom_validation, average)
                composed_callbacks.append (custom_metric)
                intels.append (custom_metric)

        if datasets.labels:
            confusion_matrix_ = confusion_matrix.ConfusionMatrixCallback (datasets.labels, datasets.validset, average = average)
            composed_callbacks.append (confusion_matrix_)
            intels.append (confusion_matrix_)

    if monitor:
        monitor, mode = monitor_options (monitor)
        composed_callbacks.append (best_metrics.BestMetricsCallback (monitor = monitor, mode = mode, intels = intels, log_path = ASSETS_DIR))
        composed_callbacks.append (tf.keras.callbacks.ModelCheckpoint (
            filepath = CHECKPOINT_FORMAT, save_weights_only = True,
            monitor = monitor, mode = mode, save_best_only = True
        ))

    if decay_rate:
        warnings.warn ('argument `decay_rate` has been deprecated, use `learning_rate`')
        assert learning_rate is None, 'ambigous parameters, remove `decay_rate`'
        learning_rate, decay_rate = decay_rate, None

    if learning_rate:
        if callable (learning_rate):
            composed_callbacks.append (tf.keras.callbacks.LearningRateScheduler (learning_rate))

        else:
            if not isinstance (learning_rate, tuple):
                raise TypeError ("learning_rate format is (initial lr, decay_rate, [decay_patience])")

            if len (learning_rate) == 3:
                if isinstance (learning_rate [1], int):
                    increasing_period = 2.0 # keras default
                    initial_lrate, period_epochs, decay_rate_per_period = learning_rate
                    scheduler = tf.keras.callbacks.LearningRateScheduler (
                        cosine_decay_restarts (initial_lrate, period_epochs, decay_rate_per_period = decay_rate_per_period, increasing_period = increasing_period)
                    )
                else:
                    learning_rate, decay_rate, decay_patience = learning_rate
                    scheduler = LRPlateauDecay (learning_rate, patience = decay_patience, factor = decay_rate)

            elif len (learning_rate) == 2:
                initial_lrate, decay_rate = learning_rate
                scheduler = scheduler = tf.keras.callbacks.LearningRateScheduler (
                    step_decay (initial_lrate, decay_rate, 1)
                )

            else:
                raise ValueError ('learning_rate must be tuple having more than 2')

            composed_callbacks.append (scheduler)

    if enable_logging:
        if os.path.isdir (LOG_DIR):
            shutil.rmtree (LOG_DIR)
            pathtool.mkdir (LOG_DIR)
        composed_callbacks.append (tf.keras.callbacks.TensorBoard (log_dir = LOG_DIR))

    if early_stop:
        early_stop, monitor_, mode_ = early_stop, 'val_loss', "min"
        if isinstance (early_stop, tuple):
            if len (early_stop) == 3:
                patience, *mo = early_stop
            elif len (early_stop) == 2:
                patience, mo = early_stop
            else:
                raise ValueError ('unknown early_stop format')
            monitor_, mode_ = monitor_options (mo)
        else:
            patience = early_stop

        composed_callbacks.append (tf.keras.callbacks.EarlyStopping (monitor = monitor_, mode = mode_, patience = patience, verbose = True, restore_best_weights = True))

    for idx, entity in enumerate (plots):
        composed_callbacks.append (plot_progress.PlotProgress (entity=entity, save_dir = ASSETS_DIR))

    composed_callbacks.append (CSVLogger (os.path.join (ASSETS_DIR, 'train.csv'), append=True, separator=','))
    return composed_callbacks


# shortcus ----------------------------------------------
def lambdas (
        train_dir, datasets,
        learning_rate = (1e-3, 1.),
        early_stop = 20,
        monitor = 'val_loss',
        plots = ['loss'],
        reset_train_dir = False,
        **kargs
):
    return conventional (
        train_dir, datasets,
        monitor = monitor,
        early_stop = early_stop,
        learning_rate = learning_rate,
        plots = plots,
        reset_train_dir = reset_train_dir,
        custom_metric = None,
        custom_validation = False,
        **kargs
    )

def conventional (
        train_dir, datasets,
        learning_rate = (1e-3, 1.),
        early_stop = 20,
        monitor = 'val_loss',
        plots = ['loss'],
        custom_metric = 'f1',
        average = 'weighted',
        custom_validation = 'A',
        reset_train_dir = False,
        on_epoch_end = None,
        on_epoch_begin = None,
        on_batch_end = None,
        on_batch_begin = None,
        on_train_end = None,
        on_train_begin = None
):
    # reload (confusion_matrix); print ('remove reload')
    # reload (numpy_metric); print ('remove reload')
    assert monitor, 'monitor is required'
    mode = 'min' if monitor.endswith ('loss') else 'max'
    'lr' not in plots and plots.append ('lr')

    cbs = compose (
        train_dir,
        datasets,
        custom_metric = custom_metric,
        monitor = (monitor, mode),
        early_stop = early_stop,
        learning_rate = learning_rate,
        plots = plots,
        average = average,
        reset_train_dir = reset_train_dir,
        custom_validation = custom_validation
    )

    # IMP: make sure placing after clear_ouput callback
    pos = 1
    for fn in tolist (on_train_begin):
        cbs.insert (pos, LambdaCallback (on_train_begin = fn))
        pos += 1
    for fn in tolist (on_epoch_begin):
        cbs.insert (pos, LambdaCallback (on_epoch_begin = fn))
        pos += 1
    for fn in tolist (on_batch_begin):
        cbs.insert (pos, LambdaCallback (on_batch_begin = fn))
        pos += 1
    for fn in tolist (on_batch_end):
        cbs.insert (pos, LambdaCallback (on_batch_end = fn))
        pos += 1
    for fn in tolist (on_epoch_end):
        cbs.insert (pos, LambdaCallback (on_epoch_end = fn))
        pos += 1
    for fn in tolist (on_train_end):
        cbs.insert (pos, LambdaCallback (on_train_end = fn))
        pos += 1
    return cbs

matrix = f1_matrix = conventional
