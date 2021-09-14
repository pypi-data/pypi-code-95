from tensorflow.keras.callbacks import Callback
from rs4.termcolor import tc, stty_size
from tensorflow.python.keras import backend as K
from . import base
import os
import re

RX_COLOR = re.compile (r'\[[0-9]+m')

class BestMetricsCallback (base.Display, Callback):
    def __init__ (self, monitor='val_loss', mode = 'auto', intels = [], log_path = None):
        Callback.__init__(self)
        self.mode = mode
        self.monitor = monitor
        self.intels = intels
        self.log_path = log_path
        self.best_logger = None
        if log_path:
            self.best_logger = open (os.path.join (self.log_path, 'best.md'), 'a')
        if self.mode == 'auto':
            if self.monitor.endswith ('_loss'):
                self.mode = 'min'
            else:
                self.mode = 'max'
        self._reset ()

    def _reset (self):
        self.best_epoch = 0
        self.best = self.mode == 'min' and -1e+10 or 0.0
        self.bests = {}
        self.buffer = []

    def on_train_begin (self, logs=None):
        self._reset ()

    def on_train_end (self, logs=None):
        if self.best_logger:
            self.best_logger.write ('Training done.\n\n')
            self.best_logger.close ()

    def on_epoch_end (self, epoch, logs):
        logs = logs or {}
        current = logs.get (self.monitor)
        cl = tc.blue
        if self.mode == 'min':
            current = -current

        improved = False
        if current > self.best:
            improved = True
            self.buffer = []
            self.best = current
            self.best_epoch = epoch + 1
            for intel in self.intels:
                info = intel.get_info ()
                if not info:
                    continue
                self.buffer.append (info)
            cl = tc.warn
            for k, v in logs.items ():
                self.bests [k] = v

        elogs = []
        elogs.append ('{}: {:.4f}'.format (cl ('epoch'), self.best_epoch))
        for k, v in self.bests.items ():
            if v < 0.0001:
                elogs.append ('{}: {:.1e}'.format (cl (k), v))
            else:
                elogs.append ('{}: {:.4f}'.format (cl (k), v))

        buffer = []
        buffer.append ('Best ' + ' - '.join (elogs))
        for info in self.buffer:
            if isinstance (info, str):
                buffer.append (info.strip ())
            else:
                buffer.append ('\n'.join (info).strip ())

        buffer = '\n'.join (buffer)
        if improved and self.best_logger:
            lines = RX_COLOR.sub ('', buffer).replace (" - ", '\n- ').split ("\n")
            md = []
            md.append ('##### ' + lines [0][5:])
            for line in lines [1:]:
                try:
                    k, v = line.split (":", 1)
                except ValueError:
                    continue
                md.append ("- {}: {}".format (k [2:], v))
            self.best_logger.write ("\n".join (md) + '\n')
            self.best_logger.write (('---------') + '\n')
            self.best_logger.flush ()
        print (buffer)
        self.draw_line ()
