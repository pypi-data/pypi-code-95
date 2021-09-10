# -*- coding: utf-8 -*-

class AppCloudera(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppClouderaInstance</a:schema> objects as values.
	<a:schema>AppClouderaInstance</a:schema> objects are divided into head nodes
	and data nodes.
	"""

	def __init__(self, headNodes, dataNodes):
		self.headNodes = headNodes;
		self.dataNodes = dataNodes;


	"""
	The <a:schema>AppClouderaInstance</a:schema> objects, part of the head nodes
	group.
	"""
	headNodes = [];

	"""
	The <a:schema>AppClouderaInstance</a:schema> objects, part of the data nodes
	group.
	"""
	dataNodes = [];

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
