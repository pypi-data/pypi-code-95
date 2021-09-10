# -*- coding: utf-8 -*-

class ThresholdSpecificsInstance(object):
	"""
	An object which contains specific custonmization properties for
	<a:schema>Threshold</a:schema> of type "instance_metrics"
	"""

	def __init__(self, measurement_type, type):
		self.measurement_type = measurement_type;
		self.type = type;


	"""
	The measurement type which the <a:schema>Threshold</a:schema> is monitoring.
	"""
	measurement_type = None;

	"""
	The schema type
	"""
	type = None;
