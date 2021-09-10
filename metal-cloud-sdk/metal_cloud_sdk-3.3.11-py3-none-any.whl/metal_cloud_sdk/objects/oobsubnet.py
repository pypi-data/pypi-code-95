# -*- coding: utf-8 -*-

class OOBSubnet(object):
	"""
	The out of band subnet for the server remote access IP addresses
	"""

	def __init__(self, subnet_oob_type, subnet_oob_prefix_size):
		self.subnet_oob_type = subnet_oob_type;
		self.subnet_oob_prefix_size = subnet_oob_prefix_size;


	"""
	Automatically generated and cannot be edited.
	"""
	subnet_oob_id = None;

	"""
	The name of the Datacenter
	"""
	datacenter_name = None;

	"""
	The subnet label.
	"""
	subnet_oob_label = None;

	"""
	The hexadecimal start address of the Subnet range.
	"""
	subnet_oob_range_start_hex = None;

	"""
	The hexadecimal end address of the Subnet range.
	"""
	subnet_oob_range_end_hex = None;

	"""
	The start address of the Subnet range in dotted notation for IPv4 or full
	notation for IPv6.
	"""
	subnet_oob_range_start_human_readable = None;

	"""
	The end address of the Subnet range in dotted notation for IPv4 or full
	notation for IPv6.
	"""
	subnet_oob_range_end_human_readable = None;

	"""
	The start address of the Subnet range in compressed notation for IPv6.
	"""
	subnet_oob_range_start_human_readable_compressed = None;

	"""
	The end address of the Subnet range in compressed notation for IPv6.
	"""
	subnet_oob_range_end_human_readable_compressed = None;

	"""
	The type of the Subnet.
	"""
	subnet_oob_type = None;

	"""
	The netmask in dotted notation for IPv4 or full notation for IPv6. IPv4
	example: "255.255.255.240"; IPv6 example: "
	ffff:ffff:ffff:ffff:0000:0000:0000:0000".
	"""
	subnet_oob_netmask_human_readable = None;

	"""
	The gateway in dotted notation for IPv4 or full notation for IPv6.
	"""
	subnet_oob_gateway_human_readable = None;

	"""
	The hexadecimal gateway.
	"""
	subnet_oob_gateway_hex = None;

	"""
	Subnet prefix size, such as /30, /27, etc. For IPv4 subnets can be one of:
	<code>27</code>, <code>28</code>, <code>29</code>, <code>30</code>. For IPv6
	subnet can only be <code>64</code>.
	"""
	subnet_oob_prefix_size = None;

	"""
	The schema type.
	"""
	type = None;
