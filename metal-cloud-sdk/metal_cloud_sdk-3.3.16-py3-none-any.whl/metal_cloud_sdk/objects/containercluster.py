# -*- coding: utf-8 -*-

class ContainerCluster(object):
	"""
	A group of ContainerArray infrastructure elements preconfigured for specific
	workloads or roles. Software (SaaS) is automatically installed.
	"""

	def __init__(self, container_platform_id, container_cluster_type):
		self.container_platform_id = container_platform_id;
		self.container_cluster_type = container_cluster_type;


	"""
	The ContainerCluster's unique label is used to create the
	<code>container_cluster_subdomain</code>. It is editable and can be used to
	call API functions.
	"""
	container_cluster_label = None;

	"""
	Automatically created based on <code>container_cluster_label</code>. It is a
	unique reference to the ContainerCluster object.
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
	Represents the ID of the Infrastructure to which the ContainerCluster
	belongs.
	"""
	infrastructure_id = None;

	"""
	Represents the ID of the ContainerPlatform to which the ContainerCluster
	belongs.
	"""
	container_platform_id = None;

	"""
	Type of the ContainerCluster. This property is not editable.
	"""
	container_cluster_type = None;

	"""
	The status of the ContainerCluster.
	"""
	container_cluster_service_status = None;

	"""
	The software version of the application installed on the cluster.
	"""
	container_cluster_software_version = None;

	"""
	Specifies if the ContainerCluster will be automatically managed or not.
	"""
	container_cluster_automatic_management = True;

	"""
	Information about the instances and the ContainerCluster software.
	"""
	container_cluster_app = None;

	"""
	The operation type, operation status and modified ContainerCluster object.
	"""
	container_cluster_operation = None;

	"""
	Reserved for GUI users.
	"""
	container_cluster_gui_settings_json = "";

	"""
	Information about connections between the current ContainerCluster and other
	clusters.
	"""
	container_cluster_connections = [];

	"""
	The schema type
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	container_cluster_change_id = None;
