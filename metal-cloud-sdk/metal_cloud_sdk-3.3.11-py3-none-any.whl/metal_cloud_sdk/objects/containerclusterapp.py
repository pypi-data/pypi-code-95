# -*- coding: utf-8 -*-

class ContainerClusterApp(object):
	"""
	Information about the ContainerCluster's Containers and its application.
	"""

	def __init__(self, container_cluster_app):
		self.container_cluster_app = container_cluster_app;


	"""
	The ContainerCluster's Containers and application information.
	"""
	container_cluster_app = None;

	"""
	The schema type
	"""
	type = None;
