# -*- coding: utf-8 -*-

class InstanceInterface(object):
	"""
	Instance interfaces are created automatically when instances are created.
	Subnets are added on networks and then IP addresses are associated
	automatically or manually through the API to instance interfaces.
	"""

	def __init__(self):
		pass;


	"""
	The instance_interface's label which is unique and it is used to form the
	<code>instance_interface_subdomain</code>. Can be used to call API
	functions.
	"""
	instance_interface_label = None;

	"""
	Automatically created based on <code>instance_interface_label</code>. It is
	a unique reference to the InstanceInterface object.
	"""
	instance_interface_subdomain = None;

	"""
	The ID of the instance interface.
	"""
	instance_interface_id = None;

	"""
	The ID of the instance to which the interface belongs.
	"""
	instance_id = None;

	"""
	The ID of the network to which the instance's interface is connected.
	"""
	network_id = None;

	"""
	Array of interface indexes which are part of a link aggregation together
	with this interface. The current interface is never included in this array,
	even if part of a link aggregation.
	"""
	instance_interface_lagg_indexes = [];

	"""
	Shows the index of the interface. Numbering starts at 0.
	"""
	instance_interface_index = None;

	"""
	Shows the capacity of the instance.
	"""
	instance_interface_capacity_mbps = None;

	"""
	The status of the instance interface.
	"""
	instance_interface_service_status = None;

	"""
	The corresponding <a:schema>ServerInterface</a:schema> object.
	"""
	server_interface = None;

	"""
	The operation type, operation status and modified Instance Interface object.
	"""
	instance_interface_operation = None;

	"""
	All <a:schema>IP</a:schema> objects from the instance interface.
	"""
	instance_interface_ips = [];

	"""
	The schema type.
	"""
	type = None;

	"""
	This value helps check against edit requests on expired objects.
	"""
	instance_interface_change_id = None;

	"""
	Instance interface acl identifier
	"""
	instance_interface_acl_identifier = None;

	"""
	instance_interface_gui_settings_json
	"""
	instance_interface_gui_settings_json = None;

	"""
	instance_interface_updated_timestamp
	"""
	instance_interface_updated_timestamp = None;

	"""
	instance_interface_san_ip_human_readable
	"""
	instance_interface_san_ip_human_readable = None;

	"""
	dns_subdomain_permanent_id
	"""
	dns_subdomain_permanent_id = None;

	"""
	infrastructure_id
	"""
	infrastructure_id = None;

	"""
	instance_interface_san_netmask_human_readable
	"""
	instance_interface_san_netmask_human_readable = None;

	"""
	instance_interface_force_quarantine_during_deploy
	"""
	instance_interface_force_quarantine_during_deploy = False;

	"""
	instance_interface_dirty_bit
	"""
	instance_interface_dirty_bit = False;

	"""
	instance_interface_is_api_private
	"""
	instance_interface_is_api_private = False;

	"""
	instance_interface_subdomain_permanent
	"""
	instance_interface_subdomain_permanent = None;

	"""
	server_interface_id
	"""
	server_interface_id = None;

	"""
	instance_interface_san_gateway_human_readable
	"""
	instance_interface_san_gateway_human_readable = None;

	"""
	network_equipment_subnet_pool_san_id
	"""
	network_equipment_subnet_pool_san_id = None;

	"""
	instance_interface_created_timestamp
	"""
	instance_interface_created_timestamp = None;

	"""
	instance_interface_vlan_identifier
	"""
	instance_interface_vlan_identifier = None;

	"""
	dns_subdomain_id
	"""
	dns_subdomain_id = None;

	"""
	instance_interface_subnet_pool_san_index
	"""
	instance_interface_subnet_pool_san_index = None;
