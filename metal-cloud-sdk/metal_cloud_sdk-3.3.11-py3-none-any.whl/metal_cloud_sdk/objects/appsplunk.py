# -*- coding: utf-8 -*-

class AppSplunk(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppSplunkInstance</a:schema> objects as values.
	<a:schema>AppSplunkInstance</a:schema> objects are divided into search heads
	and indexers.
	"""

	def __init__(self, searchHeads, indexers):
		self.searchHeads = searchHeads;
		self.indexers = indexers;


	"""
	The <a:schema>AppSplunkInstance</a:schema> objects, part of the search head
	group.
	"""
	searchHeads = [];

	"""
	The <a:schema>AppSplunkInstance</a:schema> objects, part of the indexers
	group.
	"""
	indexers = [];

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
