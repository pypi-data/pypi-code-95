# -*- coding: utf-8 -*-

class AppDatameer(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppDatameerInstance</a:schema> objects as values.
	<a:schema>AppDatameerInstance</a:schema> objects are divided into head nodes
	and data nodes.
	"""

	def __init__(self, datameer_nodes):
		self.datameer_nodes = datameer_nodes;


	"""
	The <a:schema>AppDatameerInstance</a:schema> objects.
	"""
	datameer_nodes = [];

	"""
	The admin username on the cluster.
	"""
	admin_username = None;

	"""
	The initial admin password on the cluster.
	"""
	admin_initial_password = None;

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
