# -*- coding: utf-8 -*-

class ContainerPlatform(object):
	"""
	A centralised view of all child ContainerArray and Container products.
	"""

	def __init__(self, container_platform_hosts):
		self.container_platform_hosts = container_platform_hosts;


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
	The maximum number of hosts that should be used for all existing or future
	child ContainerArray products.
	"""
	container_platform_maximum_hosts_count = 10;

	"""
	The desired minimum number of hosts that should be used for all existing or
	future child ContainerArray products.
	"""
	container_platform_minimum_hosts_count = 0;

	"""
	The ID of the ContainerPlatform which can be used instead of the
	<code>container_platform_label</code> or
	<code>container_platform_subdomain</code> when calling the API functions. It
	is automatically generated and cannot be edited.
	"""
	container_platform_id = None;

	"""
	Represents the infrastructure ID to which the ContainerPlatform belongs.
	"""
	infrastructure_id = None;

	"""
	Represents the capacity of the Data Drive.
	"""
	container_platform_data_drive_size_mbytes = 102400;

	"""
	The status of the ContainerPlatform.
	"""
	container_platform_service_status = None;

	"""
	The operation type, operation status and modified ContainerPlatform object.
	"""
	container_platform_operation = None;

	"""
	Reserved for GUI users.
	"""
	container_platform_gui_settings_json = "";

	"""
	When set to true, all firewall rules on the underlying hosts are removed and
	the firewall rules specified in the instance_array_firewall_rules property
	are applied on the servers. When set to false, the firewall rules specified
	in the instance_array_firewall_rules property are ignored. The feature only
	works for drives that are using a supported OS template.
	"""
	container_platform_firewall_managed = True;

	"""
	Contains the hardware configuration for this ContainerPlatform.
	"""
	container_platform_hardware_configuration = None;

	"""
	Information about hosts regarding servers to allocate
	"""
	container_platform_hosts = [];

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

	"""
	Contains the resource report of the ContainerPlatform.
	"""
	container_platform_resource_report = None;
