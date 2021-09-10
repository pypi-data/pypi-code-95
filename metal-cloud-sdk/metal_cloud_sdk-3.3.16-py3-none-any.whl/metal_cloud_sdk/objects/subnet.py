# -*- coding: utf-8 -*-

class Subnet(object):
	"""
	A Subnet is a subdivision of a network, a range of IP addresses minus the
	first two and the last IP addresses (network, gateway, and broadcast,
	respectively).
	"""

	def __init__(self, subnet_type, subnet_prefix_size):
		self.subnet_type = subnet_type;
		self.subnet_prefix_size = subnet_prefix_size;


	"""
	The ID of the network to which the Subnet belongs.
	"""
	network_id = None;

	"""
	The Subnet's label which is unique and it is used to form the
	<code>subnet_subdomain</code>. Can be used to call API functions.
	"""
	subnet_label = None;

	"""
	Automatically created based on <code>subnet_label</code>. It is a unique
	reference to the Subnet object.
	"""
	subnet_subdomain = None;

	"""
	The ID of the Subnet which can be used instead of the
	<code>subnet_label</code> or <code>subnet_subdomain</code> when calling the
	API functions. It is automatically generated and cannot be edited.
	"""
	subnet_id = None;

	"""
	The hexadecimal start address of the Subnet range.
	"""
	subnet_range_start_hex = None;

	"""
	The hexadecimal end address of the Subnet range.
	"""
	subnet_range_end_hex = None;

	"""
	The start address of the Subnet range in dotted notation for IPv4 or full
	notation for IPv6.
	"""
	subnet_range_start_human_readable = None;

	"""
	The end address of the Subnet range in dotted notation for IPv4 or full
	notation for IPv6.
	"""
	subnet_range_end_human_readable = None;

	"""
	The type of the Subnet.
	"""
	subnet_type = None;

	"""
	The ID of the associated infrastructure.
	"""
	infrastructure_id = None;

	"""
	The ID of a cluster in the same infrastructure. This property is reserved
	for subnets with subnet_automatic_allocation=0, subnet_destination='wan' and
	(for now) subnet_type='ipv4'.
	"""
	cluster_id = None;

	"""
	The netmask in dotted notation for IPv4 or full notation for IPv6. IPv4
	example: "255.255.255.240"; IPv6 example: "
	ffff:ffff:ffff:ffff:0000:0000:0000:0000".
	"""
	subnet_netmask_human_readable = None;

	"""
	The gateway in dotted notation for IPv4 or full notation for IPv6.
	"""
	subnet_gateway_human_readable = None;

	"""
	The hexadecimal gateway.
	"""
	subnet_gateway_hex = None;

	"""
	Subnet prefix size, such as /30, /27, etc. For IPv4 subnets can be one of:
	<code>27</code>, <code>28</code>, <code>29</code>, <code>30</code>. For IPv6
	subnet can only be <code>64</code>.
	"""
	subnet_prefix_size = None;

	"""
	The status of the Subnet.
	"""
	subnet_service_status = None;

	"""
	Type of the network for which the Subnet is destined.
	"""
	subnet_destination = "wan";

	"""
	The ipv4 vlan that should override the default from the WAN Network
	"""
	subnet_override_vlan_id = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Subnet was
	created. Example format: 2013-11-29T13:00:01Z.
	"""
	subnet_created_timestamp = "0000-00-00T00:00:00Z";

	"""
	ISO 8601 timestamp which holds the date and time when the Subnet was edited.
	Example format: 2013-11-29T13:00:01Z.
	"""
	subnet_updated_timestamp = "0000-00-00T00:00:00Z";

	"""
	The operation type, operation status and modified Subnet object.
	"""
	subnet_operation = None;

	"""
	Specifies if the subnet is allocated from a forced only subnet pool
	"""
	subnet_from_subnet_pool_forced_only = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	subnet_change_id = None;

	"""
	Specifies if subnet will be used for allocating IP addresses via DHCP
	"""
	subnet_automatic_allocation = True;
