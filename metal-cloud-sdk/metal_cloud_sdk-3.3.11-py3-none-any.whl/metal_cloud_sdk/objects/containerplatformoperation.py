# -*- coding: utf-8 -*-

class ContainerPlatformOperation(object):
	"""
	ContainerPlatformOperation contains information regarding the changes that
	are to be made to a product. Edit and deploy functions have to be called in
	order to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, container_platform_label, container_platform_firewall_managed, container_platform_firewall_rules, container_platform_change_id):
		self.container_platform_label = container_platform_label;
		self.container_platform_firewall_managed = container_platform_firewall_managed;
		self.container_platform_firewall_rules = container_platform_firewall_rules;
		self.container_platform_change_id = container_platform_change_id;


	"""
	The status of the deploy process.
	"""
	container_platform_deploy_status = None;

	"""
	The operation to be applied to the ContainerPlatform.
	"""
	container_platform_deploy_type = None;

	"""
	The ContainerPlatform's unique label is used to create the
	<code>container_platform_subdomain</code>. It is editable and can be used to
	call API functions.
	"""
	container_platform_label = None;

	"""
	Automatically created based on <code>container_platform_label</code>. It is
	a unique reference to the ContainerPlatform object.
	"""
	container_platform_subdomain = None;

	"""
	The desired maximum number of hosts that should be used for all existing or
	future child ContainerArray products.
	"""
	container_platform_maximum_hosts_count = 10;

	"""
	The desired minimum number of hosts that should be used for all existing or
	future child ContainerArray products.
	"""
	container_platform_minimum_hosts_count = 0;

	"""
	Represents the capacity of the Data Drive.
	"""
	container_platform_data_drive_size_mbytes = 102400;

	"""
	The ID of the ContainerPlatform which can be used instead of the
	<code>container_platform_label</code> or
	<code>container_platform_subdomain</code> when calling the API functions. It
	is automatically generated and cannot be edited.
	"""
	container_platform_id = None;

	"""
	Contains the hardware configuration for this ContainerPlatform.
	"""
	container_platform_hardware_configuration = None;

	"""
	When set to false, all firewall rules on the underlying hosts are removed
	and the firewall rules specified in the container_platform_firewall_rules
	property will no longer be applied on the underlying hosts. When set to
	true, the firewall rules specified in the container_platform_firewall_rules
	property will be applied on the underlying hosts.
	"""
	container_platform_firewall_managed = None;

	"""
	Contains the firewall rules.
	"""
	container_platform_firewall_rules = [];

	"""
	The schema type
	"""
	type = None;

	"""
	This property helps ensure that edit operations don't overwrite other, more
	recent changes made to the same object. It gets updated automatically after
	each successful edit operation.
	"""
	container_platform_change_id = None;
