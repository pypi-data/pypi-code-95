# -*- coding: utf-8 -*-

class AppStreamSets(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppStreamSets</a:schema> objects as values.
	"""

	def __init__(self, streamsets_node):
		self.streamsets_node = streamsets_node;


	"""
	The <a:schema>AppStreamSetsInstance</a:schema> object.
	"""
	streamsets_node = [];

	"""
	Container cluster software available versions.
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
	The connection strings to the StreamSets app.
	"""
	streamsets_connection_string = [];

	"""
	The default username.
	"""
	streamsets_admin_username = None;

	"""
	The default password.
	"""
	streamsets_admin_password = None;

	"""
	The schema type
	"""
	type = None;
