# -*- coding: utf-8 -*-

class AppMapR(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppMapRInstance</a:schema> objects as values.
	<a:schema>AppMapRInstance</a:schema> objects are divided into head nodes and
	data nodes.
	"""

	def __init__(self, mapr_nodes):
		self.mapr_nodes = mapr_nodes;


	"""
	The <a:schema>AppMapRInstance</a:schema> objects, part of the nodes group.
	"""
	mapr_nodes = [];

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
