from tensorflow.keras.callbacks import Callback
import matplotlib.pyplot as plt
import os
import warnings
import numpy as np

class PlotProgress (Callback):
    def __init__(self, entity = 'loss', save_dir = None):
        self.entity = entity
        self.save_path = None
        if save_dir:
            self.save_path = os.path.join (save_dir, 'plot-{}.png'.format (entity))
        self.jpy = os.getenv ("JPY_PARENT_PID")

    def on_train_begin (self, logs = {}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []
        self.fig = plt.figure ()
        self.logs = []

    def plot (self):
        plt.xlabel ("Epochs")
        plt.ylabel (self.entity.title ())
        plt.plot (self.x, self.val_losses, label="val_{}".format (self.entity))
        plt.plot (self.x, self.losses, label="{}".format (self.entity))
        if self.entity == 'lr' or self.entity.endswith ('loss'):
            plt.yscale ('log')
        plt.legend ()
        plt.tight_layout ()

    def on_epoch_end (self, epoch, logs = {}):
        self.logs.append (logs)
        self.x.append (epoch)

        val = logs.get('{}'.format (self.entity), np.nan)
        self.losses.append (val)
        val_val = logs.get('val_{}'.format (self.entity), np.nan)
        self.val_losses.append (val_val)

        self.i += 1
        if self.i == 1:
            return

        if self.i == 2 and self.entity.endswith ('loss'):
            self.losses [0] = self.losses [1] * 1.2
            self.val_losses [0] = self.val_losses [1] * 1.2

        if self.save_path:
            self.plot ()
            plt.savefig (self.save_path, dpi=100, facecolor='#eeeeee')
            plt.close ()

        if self.jpy:
            self.plot ()
            plt.show ()
            plt.close ()
