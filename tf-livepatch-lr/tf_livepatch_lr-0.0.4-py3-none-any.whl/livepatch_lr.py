import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers.schedules import *


class LiveLrSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
	"""
	Updates learning rate schedule based on config file during the training process.
	"""
	def __init__(self, check_for_update_interval,
				 lr_filename='current_lr.conf',
				 custom_objects={},
				 initial_schedule=None):
		"""
		:param check_for_update_interval: The interval the lr will be updated. Measured in **steps**.
		:param lr_filename: The file to read config from.
		:param custom_objects:
			The dict passed to `deserialize` function while loading lr schedule.
			This is typically for custom children of tf.keras.optimizers.schedules.LearningRateSchedule.
		"""
		lr_filename = Path(lr_filename)
		self.lr_filename = lr_filename
		self.check_for_update_interval = check_for_update_interval
		self.custom_objects = custom_objects
		if not lr_filename.exists():
			with open(lr_filename, 'w') as file:
				file.write(json.dumps(serialize(initial_schedule)))

		self.lr_file = open(lr_filename, 'r')
		self.base_schedule = initial_schedule
		self.logger = tf.get_logger()

	def __call__(self, step):
		return tf.numpy_function(self.call, [step], tf.float32)

	def load_config(self):
		"""
		Tries to load config file and update `base_schedule`. Logs failures with logger.error.
		"""
		try:
			self.lr_file.seek(0)
			config = json.loads(self.lr_file.read())
			self.base_schedule = deserialize(config, self.custom_objects)
			self.logger.info('LiveLrSchedule info: %s', 'loaded schedule name: {}'.format(self.base_schedule.__class__.__name__))
		except Exception as err:
			self.logger.error('LiveLrSchedule error: %s', str(err), exc_info=True)
			self.logger.error('LiveLrSchedule keeps schedule unchanged')

	def call(self, step):
		if step % self.check_for_update_interval == 0:
			self.load_config()

		return np.float32(self.base_schedule(step))
