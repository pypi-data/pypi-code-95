# -*- coding: utf-8 -*-

class InstanceArrayOperation(object):
	"""
	InstanceArrayOperation contains information regarding the changes that are
	to be made to a product. Edit and deploy functions have to be called in
	order to apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, instance_array_boot_method, instance_array_label, instance_array_instance_count, instance_array_ipv4_subnet_create_auto, instance_array_virtual_interfaces_enabled, instance_array_ip_allocate_auto, instance_array_ram_gbytes, instance_array_processor_count, instance_array_processor_core_mhz, instance_array_processor_core_count, drive_array_id_boot, instance_array_change_id, instance_array_firewall_managed, volume_template_id):
		self.instance_array_boot_method = instance_array_boot_method;
		self.instance_array_label = instance_array_label;
		self.instance_array_instance_count = instance_array_instance_count;
		self.instance_array_ipv4_subnet_create_auto = instance_array_ipv4_subnet_create_auto;
		self.instance_array_virtual_interfaces_enabled = instance_array_virtual_interfaces_enabled;
		self.instance_array_ip_allocate_auto = instance_array_ip_allocate_auto;
		self.instance_array_ram_gbytes = instance_array_ram_gbytes;
		self.instance_array_processor_count = instance_array_processor_count;
		self.instance_array_processor_core_mhz = instance_array_processor_core_mhz;
		self.instance_array_processor_core_count = instance_array_processor_core_count;
		self.drive_array_id_boot = drive_array_id_boot;
		self.instance_array_change_id = instance_array_change_id;
		self.instance_array_firewall_managed = instance_array_firewall_managed;
		self.volume_template_id = volume_template_id;


	"""
	The status of the deploy process.
	"""
	instance_array_deploy_status = None;

	"""
	Determines wether the server will boot from local drives or from NAS over
	iSCSI.
	"""
	instance_array_boot_method = None;

	"""
	The operation applied to the InstanceArray.
	"""
	instance_array_deploy_type = None;

	"""
	The InstanceArray's unique label is used to create the
	<code>instance_array_subdomain</code>. It is editable and can be used to
	call API functions.
	"""
	instance_array_label = None;

	"""
	Automatically created based on <code>instance_array_label</code>. It is a
	unique reference to the InstanceArray object.
	"""
	instance_array_subdomain = None;

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
	instance_array_instance_count = None;

	"""
	If <code>true</code> and no Subnet has already been allocated, a public IPv4
	will be allocated. If there are no Subnets with free IPs available, a public
	Subnet will be automatically created, as many times as needed.
	"""
	instance_array_ipv4_subnet_create_auto = None;

	"""
	Enable virtual interfaces
	"""
	instance_array_virtual_interfaces_enabled = None;

	"""
	Automatically allocate IP addresses to child Instance's InstanceInterface
	elements.
	"""
	instance_array_ip_allocate_auto = None;

	"""
	The minimum RAM capacity of each instance.
	"""
	instance_array_ram_gbytes = None;

	"""
	The CPU count on each instance.
	"""
	instance_array_processor_count = None;

	"""
	The minimum clock speed of a CPU.
	"""
	instance_array_processor_core_mhz = None;

	"""
	The minimum cores of a CPU.
	"""
	instance_array_processor_core_count = None;

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
	ISO 8601 timestamp which holds the date and time when the InstanceArray was
	edited. Example format: 2013-11-29T13:00:01Z.
	"""
	instance_array_updated_timestamp = None;

	"""
	The Drive array ID associated to the InstanceArray.
	"""
	drive_array_id_boot = None;

	"""
	Reserved for GUI users.
	"""
	instance_array_gui_settings_json = None;

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
	An array of <a:schema>InstanceArrayInterfaceOperation</a:schema> objects
	indexed from 0 to 3.
	"""
	instance_array_interfaces = [];

	"""
	When set to false, all firewall rules on the server are removed and the
	firewall rules specified in the instance_array_firewall_rules property will
	no longer be applied on the server. When set to true, the firewall rules
	specified in the instance_array_firewall_rules property will be applied on
	the server.
	"""
	instance_array_firewall_managed = None;

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
	The volume template ID or name. 
	"""
	volume_template_id = None;

	"""
	Server group name label for ProjectAPI feature.
	"""
	server_group_name = None;

	"""
	Object containing custom variables and variable overrides.
	"""
	instance_array_custom_variables = {};
