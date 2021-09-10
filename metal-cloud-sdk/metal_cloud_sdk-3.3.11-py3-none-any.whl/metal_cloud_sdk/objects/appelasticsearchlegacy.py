# -*- coding: utf-8 -*-

class AppElasticsearchLegacy(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppElasticsearchInstance</a:schema> objects as values.
	<a:schema>AppElasticsearchInstance</a:schema> objects are divided into
	master nodes and data nodes.
	"""

	def __init__(self, masterNodes, dataNodes):
		self.masterNodes = masterNodes;
		self.dataNodes = dataNodes;


	"""
	The <a:schema>AppElasticsearchInstance</a:schema> objects, part of the
	master nodes group.
	"""
	masterNodes = [];

	"""
	The <a:schema>AppElasticsearchInstance</a:schema> objects, part of the data
	nodes group.
	"""
	dataNodes = [];

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
