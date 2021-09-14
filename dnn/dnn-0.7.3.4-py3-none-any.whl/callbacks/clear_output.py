from tensorflow.keras.callbacks import Callback
from tensorflow.python.keras import backend as K
import os

class ClearOutput (Callback):
    def on_epoch_end (self, epoch, logs = {}):
        logs = logs or {}
        if 'lr' not in logs:
            logs['lr'] = K.get_value(self.model.optimizer.lr)

        if os.getenv ("JPY_PARENT_PID"):
            from IPython.display import clear_output
            clear_output (wait = True)
