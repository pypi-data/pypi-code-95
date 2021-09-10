# -*- coding: utf-8 -*-

class AppZoomdata(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppZoomdataInstance</a:schema> objects as values.
	"""

	def __init__(self, zoomdata_node):
		self.zoomdata_node = zoomdata_node;


	"""
	The <a:schema>AppZoomdataInstance</a:schema> object which represents the
	Master.
	"""
	zoomdata_node = [];

	"""
	The URL to access Zoomdata.
	"""
	zoomdata_url = None;

	"""
	Cluster software available versions.
	"""
	container_cluster_software_available_versions = [];

	"""
	The software version detected on the container cluster.
	"""
	container_cluster_software_version = None;

	"""
	Array of compatible and connectable clusters.
	"""
	connectable_container_clusters = [];

	"""
	The schema type
	"""
	type = None;
