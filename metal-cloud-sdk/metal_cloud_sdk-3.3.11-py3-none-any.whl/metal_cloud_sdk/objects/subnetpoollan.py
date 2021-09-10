# -*- coding: utf-8 -*-

class SubnetPoolLAN(object):
	"""
	"""

	def __init__(self, subnet_pool_lan_prefix_human_readable, subnet_pool_lan_prefix_size, subnet_pool_lan_type, subnets_prefix_size):
		self.subnet_pool_lan_prefix_human_readable = subnet_pool_lan_prefix_human_readable;
		self.subnet_pool_lan_prefix_size = subnet_pool_lan_prefix_size;
		self.subnet_pool_lan_type = subnet_pool_lan_type;
		self.subnets_prefix_size = subnets_prefix_size;


	"""
	The network prefix in human readable format.
	"""
	subnet_pool_lan_prefix_human_readable = None;

	"""
	The subnet pool prefix size value; ex: /24.
	"""
	subnet_pool_lan_prefix_size = None;

	"""
	Must be <code>ipv4</code> or <code>ipv6</code>.
	"""
	subnet_pool_lan_type = None;

	"""
	The start address of the Subnet pool range in dotted notation for IPv4 or
	full notation for IPv6.
	"""
	subnet_pool_lan_range_start_human_readable = None;

	"""
	The end address of the Subnet pool range in dotted notation for IPv4 or full
	notation for IPv6.
	"""
	subnet_pool_lan_range_end_human_readable = None;

	"""
	The underyling subnets prefix size value; ex: /24.
	"""
	subnets_prefix_size = None;

	"""
	The schema type.
	"""
	type = None;
