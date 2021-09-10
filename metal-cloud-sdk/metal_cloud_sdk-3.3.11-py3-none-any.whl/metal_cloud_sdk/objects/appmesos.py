# -*- coding: utf-8 -*-

class AppMesos(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppMesosInstance</a:schema> objects as values.
	"""

	def __init__(self, mesos_headnodes, mesos_slavenodes):
		self.mesos_headnodes = mesos_headnodes;
		self.mesos_slavenodes = mesos_slavenodes;


	"""
	The <a:schema>AppMesosInstance</a:schema> objects.
	"""
	mesos_headnodes = [];

	"""
	The <a:schema>AppMesosInstance</a:schema> objects.
	"""
	mesos_slavenodes = [];

	"""
	Cluster software available versions.
	"""
	cluster_software_available_versions = [];

	"""
	The software version detected on the cluster.
	"""
	cluster_software_version = None;

	"""
	Array of compatible and connectable clusters.
	"""
	connectable_clusters = [];

	"""
	The schema type
	"""
	type = None;
