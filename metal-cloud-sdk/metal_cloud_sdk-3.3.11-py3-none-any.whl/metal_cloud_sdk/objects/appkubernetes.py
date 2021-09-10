# -*- coding: utf-8 -*-

class AppKubernetes(object):
	"""
	Kubernetes cluster.
	"""

	def __init__(self, kubernetes_nodes, kubernetes_master):
		self.kubernetes_nodes = kubernetes_nodes;
		self.kubernetes_master = kubernetes_master;


	"""
	"""
	kubernetes_nodes = [];

	"""
	"""
	kubernetes_master = [];

	"""
	The admin username on the cluster.
	"""
	admin_username = None;

	"""
	The initial admin password on the cluster.
	"""
	admin_initial_password = None;

	"""
	Cluster software available versions.
	"""
	cluster_software_available_versions = [];

	"""
	The software version detected on the cluster.
	"""
	cluster_software_version = None;

	"""
	The schema type
	"""
	type = None;
