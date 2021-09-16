import tensorflow as tf
from pyhectiqlab import Run

class LabCallback(tf.keras.callbacks.Callback):

    def __init__(self, run: Run, annots: dict = {'train': '', 'val': ''}):
        self._run = run
        self.epoch = 0
        self.global_step = 0
        self.annots = annots
        assert 'train' in annots, 'annots must contains the key train'
        assert 'val' in annots, 'annots must contains the key val'

    def on_train_begin(self, logs=None):
        self._run.training()

    def on_train_end(self, logs=None):
        self._run.completed()

    def on_epoch_begin(self, epoch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):
        self.epoch += 1

    def on_train_batch_end(self, batch, logs=None):
        self.global_step += 1
        for metric in logs.keys():
            metric_val = logs[metric]
            self._run.add_metrics(f"{metric}{self.annots['train']}", value=metric_val, step=self.global_step)

    def on_test_batch_end(self, batch, logs=None):
        for metric in logs.keys():
            metric_val = logs[metric]
            self._run.add_metrics(f"{metric}{self.annots['val']}", value=metric_val, step=self.global_step)

    def on_train_batch_begin(self, batch, logs=None):
        pass