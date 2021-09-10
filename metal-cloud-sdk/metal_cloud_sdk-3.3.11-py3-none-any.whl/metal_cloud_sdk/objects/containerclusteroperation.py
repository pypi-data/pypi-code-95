# -*- coding: utf-8 -*-

class ContainerClusterOperation(object):
	"""
	ContainerClusterOperation contains information regarding the changes that
	are to be made to a product. Edit and deploy functions have to be called in
	order to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, container_cluster_label, container_cluster_change_id, container_cluster_software_version):
		self.container_cluster_label = container_cluster_label;
		self.container_cluster_change_id = container_cluster_change_id;
		self.container_cluster_software_version = container_cluster_software_version;


	"""
	The status of the deploy process.
	"""
	container_cluster_deploy_status = None;

	"""
	The operation applied to the ContainerCluster.
	"""
	container_cluster_deploy_type = None;

	"""
	The ContainerCluster's unique label is used to create the
	<code>container_cluster_subdomain</code>. It is editable and can be used to
	call API functions.
	"""
	container_cluster_label = None;

	"""
	Automatically created based on <code>container_cluster_label</code>. It is a
	unique reference to the ContainerCluster object..
	"""
	container_cluster_subdomain = None;

	"""
	The ID of the ContainerCluster which can be used instead of the
	<code>container_cluster_label</code> or
	<code>container_cluster_subdomain</code> when calling the API functions. It
	is automatically generated and cannot be edited.
	"""
	container_cluster_id = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	container_cluster_change_id = None;

	"""
	The installed ContainerCluster software version.
	"""
	container_cluster_software_version = None;

	"""
	Specifies if the ContainerCluster will be automatically managed or not.
	"""
	container_cluster_automatic_management = True;

	"""
	Information about connections between the current ContainerCluster and other
	clusters.
	"""
	container_cluster_connections = [];

	"""
	The schema type
	"""
	type = None;
