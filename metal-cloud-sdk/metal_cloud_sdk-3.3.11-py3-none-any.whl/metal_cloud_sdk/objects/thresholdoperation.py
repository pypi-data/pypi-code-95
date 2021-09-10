# -*- coding: utf-8 -*-

class ThresholdOperation(object):
	"""
	ThresholdOperation contains information regarding the changes that are to be
	made to a threshold
	"""

	def __init__(self, threshold_description, threshold_value, threshold_action_repeat_interval_hours, threshold_action, threshold_bound_type, threshold_value_destination):
		self.threshold_description = threshold_description;
		self.threshold_value = threshold_value;
		self.threshold_action_repeat_interval_hours = threshold_action_repeat_interval_hours;
		self.threshold_action = threshold_action;
		self.threshold_bound_type = threshold_bound_type;
		self.threshold_value_destination = threshold_value_destination;


	"""
	A string which provides a description of the threshold.
	"""
	threshold_description = None;

	"""
	The value for the threshold
	"""
	threshold_value = None;

	"""
	The period of time in hours that must pass before another warning is issued.
	For a one time warning, null is required
	"""
	threshold_action_repeat_interval_hours = None;

	"""
	What action to be taken when the threshold is reached
	"""
	threshold_action = None;

	"""
	Defines whether the event must be triggered when the measured value is
	greater than or less than the threashold_value
	"""
	threshold_bound_type = None;

	"""
	Defines the destination for the threshold value. It can be seen as a subtype
	of the threshold_type
	"""
	threshold_value_destination = None;

	"""
	The schema type.
	"""
	type = None;
