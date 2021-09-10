# -*- coding: utf-8 -*-

class IP(object):
	"""
	An IP object contains information regarding an IP address.
	"""

	def __init__(self, ip_operation):
		self.ip_operation = ip_operation;


	"""
	The ID of the IP address.
	"""
	ip_id = None;

	"""
	The type of the IP address.
	"""
	ip_type = None;

	"""
	The IP address in natural language.
	"""
	ip_human_readable = None;

	"""
	Hexadecimal number representing an 128 or 32 bit unsigned integer.
	"""
	ip_hex = None;

	"""
	Reserved for future use.
	"""
	ip_lease_expires = None;

	"""
	Current Operation
	"""
	ip_operation = None;

	"""
	Primary IPs are the ones served by DHCP.
	"""
	ip_is_primary = None;

	"""
	Represents the Subnet this IP is allocated from.
	"""
	subnet_id = None;

	"""
	Type of the network for which the Subnet is destined.
	"""
	subnet_destination = "wan";

	"""
	The gateway in natural language.
	"""
	subnet_gateway_human_readable = None;

	"""
	The netmask in natural language.
	"""
	subnet_netmask_human_readable = None;

	"""
	Represents the instance interface this IP address is bound to.
	"""
	instance_interface_id = None;

	"""
	Extra IPs allocated by our system for internal use by switches.
	"""
	ip_is_system_reserved = None;

	"""
	The schema type
	"""
	type = None;

	"""
	This property helps ensure that edit operations don’t overwrite other,
	more recent changes made to the same object. It gets updated automatically
	after each successful edit operation.
	"""
	ip_change_id = None;
