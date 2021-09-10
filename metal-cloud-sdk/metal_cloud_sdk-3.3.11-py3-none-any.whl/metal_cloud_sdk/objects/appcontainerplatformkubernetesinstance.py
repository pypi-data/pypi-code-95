# -*- coding: utf-8 -*-

class AppContainerPlatformKubernetesInstance(object):
	"""
	Object that contains Instance application information.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the Instance associated with the node.
	"""
	instance_id = None;

	"""
	The label of the Instance associated with the node.
	"""
	instance_label = None;

	"""
	The schema type
	"""
	type = None;
