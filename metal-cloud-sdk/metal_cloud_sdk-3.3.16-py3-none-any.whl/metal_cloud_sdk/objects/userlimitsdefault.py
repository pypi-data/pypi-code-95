# -*- coding: utf-8 -*-

class UserLimitsDefault(object):
	"""
	Default user limits per user categories
	"""

	def __init__(self):
		pass;


	"""
	Default user limits: customer with NO special testing rights
	"""
	default = None;

	"""
	Default user limits: customer with special testing rights
	"""
	demo = None;

	"""
	Default user limits: paying customer
	"""
	billable = None;

	"""
	Default user limits: bigestep employee with rank >= sales
	"""
	developer = None;

	"""
	The schema type
	"""
	type = "UserLimitsDefault";
