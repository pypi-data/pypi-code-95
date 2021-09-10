# -*- coding: utf-8 -*-

class Cluster(object):
	"""
	A group of InstanceArray and DriveArray infrastructure elements
	preconfigured for specific workloads or roles. Software (SaaS) is
	automatically installed for new instances. The preinstalled software is
	informed when instances are made available or removed.
	"""

	def __init__(self, cluster_type):
		self.cluster_type = cluster_type;


	"""
	The Cluster's unique label is used to create the
	<code>cluster_subdomain</code>. It is editable and can be used to call API
	functions.
	"""
	cluster_label = None;

	"""
	Automatically created based on <code>cluster_label</code>. It is a unique
	reference to the Cluster object.
	"""
	cluster_subdomain = None;

	"""
	Automatically created based on <code>cluster_id</code>. It is a unique
	reference to the Cluster object that never changes, so it can be trusted in
	various configs. Starting with clusters created and deployed using API
	v3.2.0 it points to all the child instances in DNS.
	"""
	cluster_subdomain_permanent = None;

	"""
	The ID of the Cluster which can be used instead of the
	<code>cluster_label</code> or <code>cluster_subdomain</code> when calling
	the API functions. It is automatically generated and cannot be edited.
	"""
	cluster_id = None;

	"""
	Represents the infrastructure ID to which the Cluster belongs.
	"""
	infrastructure_id = None;

	"""
	Type of the Cluster. This property is not editable.
	"""
	cluster_type = None;

	"""
	The status of the Cluster.
	"""
	cluster_service_status = None;

	"""
	The installed cluster software version.
	"""
	cluster_software_version = None;

	"""
	Cluster services as assigned to each instance
	"""
	cluster_service_assignment = {};

	"""
	Specifies if the cluster will be automatically managed or not.
	"""
	cluster_automatic_management = True;

	"""
	Information about the instances and the Cluster software.
	"""
	cluster_app = None;

	"""
	The operation type, operation status and modified Cluster object.
	"""
	cluster_operation = None;

	"""
	Reserved for GUI users.
	"""
	cluster_gui_settings_json = "";

	"""
	Information about connections between the current Cluster and other
	clusters.
	"""
	cluster_connections = [];

	"""
	The public SSH key used for managing the Cluster.
	"""
	cluster_ssh_management_public_key = None;

	"""
	The schema type
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	cluster_change_id = None;
