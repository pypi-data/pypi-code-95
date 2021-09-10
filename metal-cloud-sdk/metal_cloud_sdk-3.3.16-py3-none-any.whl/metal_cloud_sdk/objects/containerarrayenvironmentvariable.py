# -*- coding: utf-8 -*-

class ContainerArrayEnvironmentVariable(object):
	"""
	ContainerArray environment variable.
	"""

	def __init__(self, environment_variable_name, environment_variable_value):
		self.environment_variable_name = environment_variable_name;
		self.environment_variable_value = environment_variable_value;


	"""
	Environment variable name.
	"""
	environment_variable_name = None;

	"""
	Environment variable value.
	"""
	environment_variable_value = None;

	"""
	The schema type.
	"""
	type = None;
