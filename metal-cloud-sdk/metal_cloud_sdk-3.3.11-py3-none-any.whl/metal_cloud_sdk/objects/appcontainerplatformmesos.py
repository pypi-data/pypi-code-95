# -*- coding: utf-8 -*-

class AppContainerPlatformMesos(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppContainerPlatformMesosInstance</a:schema> objects as values.
	"""

	def __init__(self, mesos_nodes):
		self.mesos_nodes = mesos_nodes;


	"""
	The <a:schema>AppContainerPlatformMesosInstance</a:schema> objects.
	"""
	mesos_nodes = [];

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
