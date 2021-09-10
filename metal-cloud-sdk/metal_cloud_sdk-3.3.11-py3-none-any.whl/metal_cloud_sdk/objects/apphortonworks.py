# -*- coding: utf-8 -*-

class AppHortonworks(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppHortonworksInstance</a:schema> objects as values.
	<a:schema>AppHortonworksInstance</a:schema> objects are divided into head
	nodes and data nodes.
	"""

	def __init__(self, hortonworks_masternodes, hortonworks_slavenodes):
		self.hortonworks_masternodes = hortonworks_masternodes;
		self.hortonworks_slavenodes = hortonworks_slavenodes;


	"""
	The <a:schema>AppHortonworksInstance</a:schema> objects, part of the head
	nodes group.
	"""
	hortonworks_masternodes = [];

	"""
	The <a:schema>AppHortonworksInstance</a:schema> objects, part of the data
	nodes group.
	"""
	hortonworks_slavenodes = [];

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
