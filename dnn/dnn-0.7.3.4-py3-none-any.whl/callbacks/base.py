import tensorflow as tf
import numpy as np
from rs4.termcolor import tc, stty_size

class Display:
    def draw_line (self):
        try:
            columns, _ = stty_size ()
        except ValueError:
            columns = 60
        print (tc.grey ('_' * columns + '\n'))


class ValiadtionSet:
    def __init__ (self, validation_data):
        self.validation_data = validation_data
        self.ys, self.logits = None, None

    def on_epoch_begin (self, epoch, logs):
        self.ys, self.logits = None, None

    def make_predictions (self):
        if isinstance (self.validation_data, tf.data.Dataset):
            validation_data = self.validation_data.as_numpy_iterator ()
        else:
            validation_data = [self.validation_data]

        self.ys = None
        multiple_output = False
        for xs, ys in validation_data:
            logits = self.model (xs, training = False)
            if isinstance (ys, tuple):
                multiple_output = True
                if self.ys is None:
                    self.ys = [[] for i in range (len (ys))]
                    self.logits = [[] for i in range (len (ys))]

                for idx, v in enumerate (ys):
                    self.ys [idx].extend (v)
                for idx, v in enumerate (logits):
                    self.logits [idx].extend (v)

            else:
                if self.ys is None:
                    self.ys = []
                    self.logits = []
                self.ys.extend (ys)
                self.logits.extend (logits)

        if multiple_output:
            self.ys = tuple ([np.array (each) for each in self.ys])
            self.logits = tuple ([np.array (each) for each in self.logits])
        else:
            self.ys = np.array (self.ys)
            self.logits = np.array (self.logits)
