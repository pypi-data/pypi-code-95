# -*- coding: utf-8 -*-

class SubnetPool(object):
	"""
	"""

	def __init__(self, subnet_pool_prefix_human_readable, subnet_pool_netmask, subnet_pool_type, subnet_pool_routable, subnet_pool_destination):
		self.subnet_pool_prefix_human_readable = subnet_pool_prefix_human_readable;
		self.subnet_pool_netmask = subnet_pool_netmask;
		self.subnet_pool_type = subnet_pool_type;
		self.subnet_pool_routable = subnet_pool_routable;
		self.subnet_pool_destination = subnet_pool_destination;


	"""
	the network prefix in human readable format.
	"""
	subnet_pool_prefix_human_readable = None;

	"""
	the netmask value; ex: /32.
	"""
	subnet_pool_netmask = None;

	"""
	must be <code>ipv4</code> or <code>ipv6</code>.
	"""
	subnet_pool_type = None;

	"""
	specifies if the IP addresses from this subnet_pool are routable.
	"""
	subnet_pool_routable = None;

	"""
	"""
	subnet_pool_forced_only = None;

	"""
	the destination of this subnet_pool. Must be one of the following:
	<code>wan</code>, <code>lan</code>, <code>san</code>, <code>oob</code>,
	<code>wan_anycast</code>.
	"""
	subnet_pool_destination = None;

	"""
	The schema type.
	"""
	type = None;
