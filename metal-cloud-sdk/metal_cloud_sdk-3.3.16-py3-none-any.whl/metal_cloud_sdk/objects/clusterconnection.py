# -*- coding: utf-8 -*-

class ClusterConnection(object):
	"""
	A Cluster Connection object.
	"""

	def __init__(self, cluster_id):
		self.cluster_id = cluster_id;


	"""
	Represents the target cluster ID of the connection.
	"""
	cluster_id = None;

	"""
	The schema type.
	"""
	type = None;
