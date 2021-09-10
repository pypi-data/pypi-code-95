# -*- coding: utf-8 -*-

class InstanceArray(object):
	"""
	An InstanceArray is a group of instances which share the same workload (thus
	enabling scalability). All instances are configured simultaneously through
	their InstanceArray. Deploying an InstanceArray has the effect of allocating
	servers to instances and activating network configurations.
	"""

	def __init__(self):
		pass;


	"""
	The InstanceArray's unique label is used to create the
	<code>instance_array_subdomain</code>. It is editable and can be used to
	call API functions.
	"""
	instance_array_label = None;

	"""
	Automatically created based on <code>instance_array_label</code>. It is a
	unique reference to the InstanceArray object. In DNS it points to all the
	child instances primary public IP addresses.
	"""
	instance_array_subdomain = None;

	"""
	Automatically created based on <code>instance_array_id</code>. It is a
	unique reference to the InstanceArray object that never changes, so it can
	be used in various configs. In DNS it points to all the child instances
	primary public IP addresses.
	"""
	instance_array_subdomain_permanent = None;

	"""
	The ID of the InstanceArray which can be used instead of the
	<code>instance_array_label</code> or <code>instance_array_subdomain</code>
	when calling the API functions. It is automatically generated and cannot be
	edited.
	"""
	instance_array_id = None;

	"""
	The number of instances to be created on the InstanceArray.
	"""
	instance_array_instance_count = 1;

	"""
	Automatically create or expand Subnet elements until the necessary IPv4
	addresses are allocated.
	"""
	instance_array_ipv4_subnet_create_auto = True;

	"""
	Enable virtual interfaces
	"""
	instance_array_virtual_interfaces_enabled = False;

	"""
	Automatically allocate IP addresses to child Instance's InstanceInterface
	elements.
	"""
	instance_array_ip_allocate_auto = True;

	"""
	The minimum RAM capacity of each instance.
	"""
	instance_array_ram_gbytes = 1;

	"""
	The CPU count on each instance.
	"""
	instance_array_processor_count = 1;

	"""
	The minimum clock speed of a CPU.
	"""
	instance_array_processor_core_mhz = 1000;

	"""
	The minimum cores of a CPU.
	"""
	instance_array_processor_core_count = 1;

	"""
	The minimum number of physical disks.
	"""
	instance_array_disk_count = 0;

	"""
	The minimum size of a single disk.
	"""
	instance_array_disk_size_mbytes = 0;

	"""
	The types of physical disks.
	"""
	instance_array_disk_types = [];

	"""
	Represents the infrastructure ID to which the InstanceArray belongs.
	"""
	infrastructure_id = None;

	"""
	The <a:schema>DriveArray</a:schema> from which the servers boot. If
	<code>null</code>, and the servers in the InstanceArray don't have local
	disks, then the instances will not boot even if
	<a:schema>DriveArray</a:schema> elements are attached.
	"""
	drive_array_id_boot = None;

	"""
	The status of the InstanceArray.
	"""
	instance_array_service_status = None;

	"""
	The operation type, operation status and modified InstanceArray object.
	"""
	instance_array_operation = None;

	"""
	An array of <a:schema>InstanceArrayInterface</a:schema> objects indexed from
	0 to 3.
	"""
	instance_array_interfaces = [];

	"""
	Determines wether the server will boot from local drives or from NAS over
	iSCSI.
	"""
	instance_array_boot_method = "pxe_iscsi";

	"""
	If not <code>null</code>, then the InstanceArray is part of the specified
	<a:schema>Cluster</a:schema>.
	"""
	cluster_id = None;

	"""
	"""
	cluster_role_group = "none";

	"""
	Reserved for GUI users.
	"""
	instance_array_gui_settings_json = "";

	"""
	ISO 8601 timestamp which holds the date and time when the InstanceArray was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_array_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the InstanceArray was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_array_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	instance_array_change_id = None;

	"""
	When set to true, all firewall rules on the server are removed and the
	firewall rules specified in the instance_array_firewall_rules property are
	applied on the server. When set to false, the firewall rules specified in
	the instance_array_firewall_rules property are ignored. The feature only
	works for drives that are using a supported OS template.
	"""
	instance_array_firewall_managed = True;

	"""
	Contains the firewall rules (an array of <a:schema>FirewallRule</a:schema>
	objects). When creating a new InstanceArray, if null, default firewall rules
	are applied (allow any source ICMP, any private IPv4, and others).
	"""
	instance_array_firewall_rules = None;

	"""
	ID of a ipv4 WAN subnetpool from which to force the subnet allocation for
	the InstanceInterfaces associated with this InstanceArray.
	"""
	network_equipment_force_subnet_pool_ipv4_wan_id = None;

	"""
	The ipv4 vlan that should override the default from the WAN Network for the
	primary ip.
	"""
	instance_array_override_ipv4_wan_vlan_id = None;

	"""
	Contains info about additional ips to be assigned to the WAN interfaces.
	"""
	instance_array_additional_wan_ipv4_json = None;

	"""
	The volume template ID (or name) to use if the servers in the InstanceArray
	have local disks. 
	"""
	volume_template_id = None;

	"""
	List of tags representative for the InstanceArray.
	"""
	instance_array_tags = [];

	"""
	Server group name label for ProjectAPI feature.
	"""
	server_group_name = None;

	"""
	Object containing custom variables and variable overrides.
	"""
	instance_array_custom_variables = {};
