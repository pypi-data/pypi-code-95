# -*- coding: utf-8 -*-

class AppVMwarevSphereInstance(object):
	"""
	Details about the Instance object specific to VMware vSphere.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the instance associated with the node.
	"""
	instance_id = None;

	"""
	The label of the instance associated with the node.
	"""
	instance_label = None;

	"""
	The status of the instance.
	"""
	instance_service_status = None;

	"""
	The subdomain of the node
	"""
	instance_hostname = None;

	"""
	The cluster UI url of the node
	"""
	instance_cluster_url = None;

	"""
	The health status of the node
	"""
	instance_health = None;

	"""
	The schema type
	"""
	type = None;
