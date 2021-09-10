# -*- coding: utf-8 -*-

class AppDatastax(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppDatastaxInstance</a:schema> objects as values.
	"""

	def __init__(self, seeds, nodes):
		self.seeds = seeds;
		self.nodes = nodes;


	"""
	The <a:schema>AppDatastaxInstance</a:schema> objects.
	"""
	seeds = [];

	"""
	The <a:schema>AppDatastaxInstance</a:schema> objects.
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
