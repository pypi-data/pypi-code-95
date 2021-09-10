# -*- coding: utf-8 -*-

class AppMapRLegacy(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppMapRInstance</a:schema> objects as values.
	<a:schema>AppMapRInstance</a:schema> objects are divided into head nodes and
	data nodes.
	"""

	def __init__(self, mapr_masternodes, mapr_slavenodes):
		self.mapr_masternodes = mapr_masternodes;
		self.mapr_slavenodes = mapr_slavenodes;


	"""
	The <a:schema>AppMapRInstance</a:schema> objects, part of the head nodes
	group.
	"""
	mapr_masternodes = [];

	"""
	The <a:schema>AppMapRInstance</a:schema> objects, part of the data nodes
	group.
	"""
	mapr_slavenodes = [];

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
