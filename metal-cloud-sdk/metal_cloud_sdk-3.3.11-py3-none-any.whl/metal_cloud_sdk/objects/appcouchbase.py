# -*- coding: utf-8 -*-

class AppCouchbase(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppCouchbaseInstance</a:schema> objects as values.
	"""

	def __init__(self, nodes):
		self.nodes = nodes;


	"""
	The <a:schema>AppCouchbaseInstance</a:schema> objects.
	"""
	nodes = [];

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
