# -*- coding: utf-8 -*-

class ClusterApp(object):
	"""
	Information about the Cluster's Instances and its application.
	"""

	def __init__(self, cluster_app):
		self.cluster_app = cluster_app;


	"""
	The Cluster's Instances and application information.
	"""
	cluster_app = None;

	"""
	The schema type
	"""
	type = None;
