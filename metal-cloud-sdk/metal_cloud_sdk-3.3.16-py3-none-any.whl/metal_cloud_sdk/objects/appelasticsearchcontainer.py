# -*- coding: utf-8 -*-

class AppElasticsearchContainer(object):
	"""
	An object which has instance labels as keys and
	<a:schema>AppElasticsearchContainer</a:schema> objects as values.
	"""

	def __init__(self, elasticsearch_node):
		self.elasticsearch_node = elasticsearch_node;


	"""
	The <a:schema>AppElasticsearchContainerInstance</a:schema> object which
	represents the Master.
	"""
	elasticsearch_node = [];

	"""
	The connection strings to the ElasticsearchContainer app.
	"""
	connection_strings = [];

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
	The default username.
	"""
	username = None;

	"""
	The default password.
	"""
	password = None;

	"""
	The name of the cluster.
	"""
	cluster_name = None;

	"""
	The schema type
	"""
	type = None;
