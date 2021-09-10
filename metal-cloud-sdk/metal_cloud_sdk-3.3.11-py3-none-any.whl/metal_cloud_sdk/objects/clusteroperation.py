# -*- coding: utf-8 -*-

class ClusterOperation(object):
	"""
	ClusterOperation contains information regarding the changes that are to be
	made to a product. Edit and deploy functions have to be called in order to
	apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, cluster_label, cluster_change_id, cluster_software_version):
		self.cluster_label = cluster_label;
		self.cluster_change_id = cluster_change_id;
		self.cluster_software_version = cluster_software_version;


	"""
	The status of the deploy process.
	"""
	cluster_deploy_status = None;

	"""
	The operation applied to the Cluster.
	"""
	cluster_deploy_type = None;

	"""
	The Cluster's unique label is used to create the
	<code>cluster_subdomain</code>. It is editable and can be used to call API
	functions.
	"""
	cluster_label = None;

	"""
	Automatically created based on <code>cluster_label</code>. It is a unique
	reference to the Cluster object..
	"""
	cluster_subdomain = None;

	"""
	The ID of the Cluster which can be used instead of the
	<code>cluster_label</code> or <code>cluster_subdomain</code> when calling
	the API functions. It is automatically generated and cannot be edited.
	"""
	cluster_id = None;

	"""
	The schema type
	"""
	type = None;

	"""
	Cluster services as assigned to each instance
	"""
	cluster_service_assignment = {};

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	cluster_change_id = None;

	"""
	The installed cluster software version.
	"""
	cluster_software_version = None;

	"""
	Specifies if the cluster will be automatically managed or not.
	"""
	cluster_automatic_management = True;

	"""
	Information about connections between the current Cluster and other
	clusters.
	"""
	cluster_connections = [];
