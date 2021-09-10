# -*- coding: utf-8 -*-

class AppContainerPlatformMesosInstance(object):
	"""
	Details about the Instance object specific to ContainerPlatformMesos.
	"""

	def __init__(self):
		pass;


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
