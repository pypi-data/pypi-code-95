# -*- coding: utf-8 -*-

class UserLimitsCustom(object):
	"""
	Contains the user limits and the fields that are marked as not default
	manualy
	"""

	def __init__(self):
		pass;


	"""
	All the user limits, with the custom limits merged over the default limits
	"""
	user_limits = None;

	"""
	Custom limits, null if no custom value exists for a limit
	"""
	custom_limits = None;

	"""
	Specifies the base type of the limit: developer > billable > demo > default
	"""
	limits_base_category = None;

	"""
	The schema type
	"""
	type = None;
