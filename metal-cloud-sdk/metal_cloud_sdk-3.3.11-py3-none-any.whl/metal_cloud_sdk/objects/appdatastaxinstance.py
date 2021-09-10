# -*- coding: utf-8 -*-

class AppDatastaxInstance(object):
	"""
	Details about the Instance object specific to Datastax.
	"""

	def __init__(self):
		pass;


	"""
	The initial admin username on the opscenter interface of the cluster.
	"""
	opscenter_username = None;

	"""
	The initial admin password on the opscenter interface of the cluster.
	"""
	opscenter_initial_password = None;

	"""
	The IP for the opscenter interface of the cluster.
	"""
	opscenter_ip = None;

	"""
	The URL for the RPC of the node.
	"""
	rpc_url = None;

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
