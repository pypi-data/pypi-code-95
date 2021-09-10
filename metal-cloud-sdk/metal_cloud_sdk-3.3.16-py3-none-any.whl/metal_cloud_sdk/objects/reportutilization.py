# -*- coding: utf-8 -*-

class ReportUtilization(object):
	"""
	Cost details for resources like instances, Drives and Subnets.
	"""

	def __init__(self, quantity, measurement_unit, cost, cost_currency):
		self.quantity = quantity;
		self.measurement_unit = measurement_unit;
		self.cost = cost;
		self.cost_currency = cost_currency;


	"""
	The amount of a resource used to calculate the costs.
	"""
	quantity = None;

	"""
	The measurement unit used to calculate the costs.
	"""
	measurement_unit = None;

	"""
	The costs of a certain resource for a period of time.
	"""
	cost = None;

	"""
	The currency used to calculate the costs.
	"""
	cost_currency = None;

	"""
	The schema type
	"""
	type = None;
