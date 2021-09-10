# -*- coding: utf-8 -*-

class SwitchDevice(object):
	"""
	Represents a switch installed in a datacenter.
	"""

	def __init__(self, datacenter_name, network_equipment_provisioner_type, network_equipment_position, network_equipment_driver, network_equipment_management_username, network_equipment_management_password, network_equipment_management_address, network_equipment_management_protocol, network_equipment_id):
		self.datacenter_name = datacenter_name;
		self.network_equipment_provisioner_type = network_equipment_provisioner_type;
		self.network_equipment_position = network_equipment_position;
		self.network_equipment_driver = network_equipment_driver;
		self.network_equipment_management_username = network_equipment_management_username;
		self.network_equipment_management_password = network_equipment_management_password;
		self.network_equipment_management_address = network_equipment_management_address;
		self.network_equipment_management_protocol = network_equipment_management_protocol;
		self.network_equipment_id = network_equipment_id;


	"""
	The datacenter where the switch device is available for use.
	"""
	datacenter_name = None;

	"""
	Provisioner of network encapsulation.
	"""
	network_equipment_provisioner_type = None;

	"""
	Specifies the position of the switch device.
	"""
	network_equipment_position = None;

	"""
	The driver used by the switch device.
	"""
	network_equipment_driver = None;

	"""
	The username used to log in to the switch device.
	"""
	network_equipment_management_username = None;

	"""
	The password used to log in to the switch device.
	"""
	network_equipment_management_password = None;

	"""
	The IPv4 address of the management port used to log in to the switch device.
	Example: 192.168.137.1
	"""
	network_equipment_management_address = None;

	"""
	The port utilized to log in to the switch device.
	"""
	network_equipment_management_port = 22;

	"""
	The management protocol of the switch device.
	"""
	network_equipment_management_protocol = None;

	"""
	Determines if the switch device requires an automatic OS installation, based
	on its architecture and vendor model.
	"""
	network_equipment_requires_os_install = False;

	"""
	The ID of the network operating system to be installed on the switch.
	"""
	volume_template_id = None;

	"""
	This is the BSI allocated string identifier, usually residing within the
	hostname field. It is optional if the <code>bAutoDescribe</code> parameter
	of <code>switch_device_create</code> is set to true.
	"""
	network_equipment_identifier_string = None;

	"""
	Network address (first IP) of the WAN IPv4 subnet. Example: 192.168.0.0
	"""
	network_equipment_primary_wan_ipv4_subnet_pool = None;

	"""
	Prefix size of the IPv4 subnet.
	"""
	network_equipment_primary_wan_ipv4_subnet_prefix_size = 22;

	"""
	Network address (first IP) of the WAN IPv6 subnet. Example:
	2a02:0cb8:0000:0000:0000:0000:0000:0000
	"""
	network_equipment_primary_wan_ipv6_subnet_pool = None;

	"""
	Prefix size of the IPv6 WAN subnet.
	"""
	network_equipment_primary_wan_ipv6_subnet_prefix_size = 53;

	"""
	Network address (first IP) of the SAN subnet.By default, the SAN subnet has
	a netmask of 21. Example: 192.168.0.0
	"""
	network_equipment_primary_san_subnet_pool = None;

	"""
	Prefix size of the SAN subnet.
	"""
	network_equipment_primary_san_subnet_prefix_size = 21;

	"""
	For example: 172.17.0.1.
	"""
	network_equipment_quarantine_subnet_start = None;

	"""
	For example: 172.17.0.254.
	"""
	network_equipment_quarantine_subnet_end = None;

	"""
	Normally always 24, by convention.
	"""
	network_equipment_quarantine_subnet_prefix_size = None;

	"""
	IPv4 address. Usually the same with the first IP in the subnet. Example:
	172.17.0.1.
	"""
	network_equipment_quarantine_subnet_gateway = None;

	"""
	Address mask of the switch device's management port. Example: 255.255.255.0
	"""
	network_equipment_management_address_mask = None;

	"""
	The gateway IP of the switch device's management port. Example:
	192.168.137.2
	"""
	network_equipment_management_address_gateway = None;

	"""
	MAC address of the switch device's management port. Example:
	00:A0:C9:14:C8:29
	"""
	network_equipment_management_mac_address = "00:00:00:00:00:00";

	"""
	Description regarding the switch device.
	"""
	network_equipment_description = None;

	"""
	The country where the switch device is physically located. Example: UK
	"""
	network_equipment_country = None;

	"""
	The city where the switch device is physically located. Example: Reading
	"""
	network_equipment_city = None;

	"""
	The datacenter where the switch device is physically located. Example: Amito
	"""
	network_equipment_datacenter = None;

	"""
	The datacenter room where the switch device is physically located. Example:
	01
	"""
	network_equipment_datacenter_room = None;

	"""
	The datacenter rack where the switch device is physically located. Example:
	A02
	"""
	network_equipment_datacenter_rack = None;

	"""
	Information regarding the switch device's physical location in the rack.
	Example: 33
	"""
	network_equipment_rack_position_upper_unit = None;

	"""
	Information regarding the switch device's physical location in the rack.
	Example: 34
	"""
	network_equipment_rack_position_lower_unit = None;

	"""
	The associated chassis rack name, if any.
	"""
	chassis_rack_id = None;

	"""
	"""
	network_equipment_tor_linked_id = None;

	"""
	Tags associated with the switch device.
	"""
	network_equipment_tags = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	Datacenter id parent.
	"""
	datacenter_id_parent = None;

	"""
	Quarantine vlan.
	"""
	network_equipment_quarantine_vlan = None;

	"""
	The switch device's serial number. Example: CN34FHC076
	"""
	network_equipment_serial_numbers = None;

	"""
	Management subnet end.
	"""
	network_equipment_management_subnet_end = None;

	"""
	Driver dump cached json.
	"""
	network_equipment_driver_dump_cached_json = None;

	"""
	Primary WAN IPv6 subnet pool id.
	"""
	network_equipment_primary_wan_ipv6_subnet_pool_id = None;

	"""
	Cached updated timestamp.
	"""
	network_equipment_cached_updated_timestamp = None;

	"""
	Cache wrapper PHPSerialize.
	"""
	network_equipment_cache_wrapper_phpserialize = None;

	"""
	Info JSON.
	"""
	network_equipment_info_json = None;

	"""
	Management subnet.
	"""
	network_equipment_management_subnet = None;

	"""
	Network equipment id
	"""
	network_equipment_id = None;

	"""
	Primary WAN IPv6 CIDR
	"""
	network_equipment_primary_wan_ipv6_subnet_cidr = None;

	"""
	Cache wrapper json.
	"""
	network_equipment_cache_wrapper_json = None;

	"""
	Management subnet prefix size.
	"""
	network_equipment_management_subnet_prefix_size = None;

	"""
	DHCP packet sniffing flag.
	"""
	network_equipment_dhcp_packet_sniffing_is_enabled = False;

	"""
	The names of the server processors.
	"""
	network_equipment_status = "active";

	"""
	Interfaces blacklist json.
	"""
	network_equipment_interfaces_blacklist_json = None;

	"""
	Management subnet start.
	"""
	network_equipment_management_subnet_start = None;

	"""
	Controller id.
	"""
	network_equipment_controller_id = None;

	"""
	Management subnet gateway.
	"""
	network_equipment_management_subnet_gateway = None;

	"""
	This flag marks this switch as usable on external connections.
	"""
	network_equipment_is_border_device = False;

	"""
	Uplink IP addresses json.
	"""
	network_equipment_uplink_ip_addresses_json = None;
