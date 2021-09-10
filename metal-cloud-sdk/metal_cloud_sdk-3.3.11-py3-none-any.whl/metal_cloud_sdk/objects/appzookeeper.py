# -*- coding: utf-8 -*-

class AppZookeeper(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppZookeeperInstance</a:schema> objects as values.
	"""

	def __init__(self, zookeeper_nodes):
		self.zookeeper_nodes = zookeeper_nodes;


	"""
	The <a:schema>AppZookeeperInstance</a:schema> object which represents the
	Master.
	"""
	zookeeper_nodes = [];

	"""
	The connection strings to the Zookeeper app.
	"""
	zookeeper_connection_strings = [];

	"""
	Cluster software available versions.
	"""
	container_cluster_software_available_versions = [];

	"""
	The software version detected on the container cluster.
	"""
	container_cluster_software_version = None;

	"""
	Array of compatible and connectable clusters.
	"""
	connectable_container_clusters = [];

	"""
	The schema type
	"""
	type = None;
