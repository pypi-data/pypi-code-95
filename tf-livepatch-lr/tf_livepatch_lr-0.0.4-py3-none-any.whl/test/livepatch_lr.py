import os
from unittest import TestCase
from tempfile import NamedTemporaryFile
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.optimizers.schedules import LearningRateSchedule, PolynomialDecay
from tensorflow.keras.callbacks import LambdaCallback
import tensorflow.keras.layers as layers

from tf_livepatch_lr.livepatch_lr import LiveLrSchedule


class ConstantLrSchedule(LearningRateSchedule):
	def __init__(self, c):
		super(ConstantLrSchedule, self).__init__()
		self.c = c

	def __call__(self, step):
		return self.c

	def get_config(self):
		return {'c': self.c}


class TestLiveLrSchedule(TestCase):

	def setUp(self):
		tf.get_logger().setLevel('INFO')

	def test_init(self):
		lr = PolynomialDecay(0.01, 100)
		lr = LiveLrSchedule(50, initial_schedule=lr)

	def test_call(self):
		initial_config_file = open(Path('livepatch_lr') / 'polynomial_decay.json')
		last_config_file = open(Path('livepatch_lr') / 'constant.json')

		temp_config_file = NamedTemporaryFile('w+', delete=False)
		temp_config_file.write(initial_config_file.read())
		temp_config_file.close()

		self.xs = np.ones((1, 1, 1), np.float32)
		self.ys = self.xs.copy()
		self.model = Sequential([
			layers.Dense(1)
		])

		def on_epoch_end(epoch, logs):
			if epoch == 5:
				with open(temp_config_file.name, 'w') as f:
					f.truncate(0)
					f.seek(0)
					f.write(last_config_file.read())

		change_config_callback = LambdaCallback(on_epoch_end=on_epoch_end)

		lr = LiveLrSchedule(8, temp_config_file.name, custom_objects={'ConstantLrSchedule': ConstantLrSchedule})
		self.model.compile(SGD(lr), 'mse', run_eagerly=False)
		self.model.fit(self.xs, self.ys, epochs=10, callbacks=[change_config_callback])
		initial_config_file.close()
		last_config_file.close()
		os.unlink(temp_config_file.name)

		self.assertEqual(lr.base_schedule.__class__.__name__, 'ConstantLrSchedule')
