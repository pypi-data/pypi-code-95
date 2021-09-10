# -*- coding: utf-8 -*-

class AppMesosInstance(object):
	"""
	Details about the Instance object specific to Mesos.
	"""

	def __init__(self):
		pass;


	"""
	The initial admin username for the Mesos interface of the cluster.
	"""
	admin_username = None;

	"""
	The initial admin password for the Mesos interface of the cluster.
	"""
	admin_initial_password = None;

	"""
	The IP of the Mesos interface of the cluster.
	"""
	mesos_ip = None;

	"""
	The Mesos version installed on the cluster.
	"""
	mesos_version = None;

	"""
	The IP of the Marathon interface of the cluster.
	"""
	marathon_ip = None;

	"""
	The Marathon version installed on the cluster.
	"""
	marathon_version = None;

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
