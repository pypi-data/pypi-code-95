# -*- coding: utf-8 -*-

class DeployOptions(object):
	"""
	Object used to specify the server types for new Instances provisioned on the
	InstanceArrays of an Infrastructure.
	"""

	def __init__(self, instance_array):
		self.instance_array = instance_array;


	"""
	Server types for new Instances provisioned on a single InstanceArray.
	"""
	instance_array = {};

	"""
	The schema type
	"""
	type = None;
