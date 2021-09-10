# -*- coding: utf-8 -*-

class DatasetSubscription(object):
	"""
	A subscription to a Dataset.
	"""

	def __init__(self):
		pass;


	"""
	The Dataset for which the subscription was created.
	"""
	dataset = None;

	"""
	The ID of the user that owns the dataset subscription.
	"""
	user_id = None;

	"""
	The ID of the dataset subscription.
	"""
	dataset_subscription_id = None;

	"""
	The schema type.
	"""
	type = None;
