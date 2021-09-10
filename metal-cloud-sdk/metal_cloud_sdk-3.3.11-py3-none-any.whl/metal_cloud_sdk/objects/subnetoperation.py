# -*- coding: utf-8 -*-

class SubnetOperation(object):
	"""
	SubnetOperation contains information regarding the changes that are to be
	made to a product. Edit and deploy functions have to be called in order to
	apply the changes. The operation type and status are unique to each
	operation object.
	"""

	def __init__(self, subnet_label, subnet_type, network_id, subnet_prefix_size, subnet_destination, subnet_change_id):
		self.subnet_label = subnet_label;
		self.subnet_type = subnet_type;
		self.network_id = network_id;
		self.subnet_prefix_size = subnet_prefix_size;
		self.subnet_destination = subnet_destination;
		self.subnet_change_id = subnet_change_id;


	"""
	The operation applied to the Subnet.
	"""
	subnet_deploy_type = None;

	"""
	The status of the deploy process.
	"""
	subnet_deploy_status = None;

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
	The ID of the network to which the Subnet belongs.
	"""
	network_id = None;

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
	<code>27</code>, <code>28</code>, <code>29</code>, <code>30</code>.
	"""
	subnet_prefix_size = None;

	"""
	ISO 8601 timestamp which holds the date and time when the Subnet was edited.
	Example format: 2013-11-29T13:00:01Z.
	"""
	subnet_updated_timestamp = None;

	"""
	Type of the network for which the Subnet is destined.
	"""
	subnet_destination = None;

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
