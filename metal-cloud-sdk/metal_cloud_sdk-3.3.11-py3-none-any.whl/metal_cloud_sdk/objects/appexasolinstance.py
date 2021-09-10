# -*- coding: utf-8 -*-

class AppExasolInstance(object):
	"""
	Details about the Instance object specific to Exasol.
	"""

	def __init__(self):
		pass;


	"""
	The initial admin username on the interface of the cluter.
	"""
	admin_username = None;

	"""
	The initial admin password on the interface of the cluster.
	"""
	admin_initial_password = None;

	"""
	The IP for the interface of the cluster.
	"""
	exaoperation_ip = None;

	"""
	The ID of the instance associated with the node.
	"""
	instance_id = None;

	"""
	The label of the instance associated with the node.
	"""
	instance_label = None;

	"""
	The schema type
	"""
	type = None;
