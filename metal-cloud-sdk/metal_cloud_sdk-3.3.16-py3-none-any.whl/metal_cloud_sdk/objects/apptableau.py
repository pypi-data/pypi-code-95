# -*- coding: utf-8 -*-

class AppTableau(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppTableauInstance</a:schema> objects as values.
	"""

	def __init__(self):
		pass;


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
