# -*- coding: utf-8 -*-

class AppContainerPlatformKubernetes(object):
	"""
	Object that contains Cluster application information.
	"""

	def __init__(self, kubernetes_masters):
		self.kubernetes_masters = kubernetes_masters;


	"""
	The Kubernetes UI username.
	"""
	admin_username = None;

	"""
	The Kubernetes UI password.
	"""
	admin_password = None;

	"""
	The <a:schema>AppContainerPlatformKubernetesInstance</a:schema> objects.
	"""
	kubernetes_masters = [];

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
