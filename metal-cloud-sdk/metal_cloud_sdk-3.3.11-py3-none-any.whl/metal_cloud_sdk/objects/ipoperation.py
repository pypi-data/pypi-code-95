# -*- coding: utf-8 -*-

class IPOperation(object):
	"""
	IPOperation contains information regarding the changes that are to be made
	to a product. Edit and deploy functions have to be called in order to apply
	the changes. The operation type and status are unique to each operation
	object.
	"""

	def __init__(self, ip_label, ip_change_id):
		self.ip_label = ip_label;
		self.ip_change_id = ip_change_id;


	"""
	Represents the instance interface this IP address is bound to.
	"""
	instance_interface_id = None;

	"""
	The status of the deploy process.
	"""
	ip_deploy_status = None;

	"""
	The operation applied to the IP.
	"""
	ip_deploy_type = None;

	"""
	The ID of the IP address. It can be used instead of the
	<code>ip_label</code> or <code>subnet_subdomain</code> when calling API
	functions. It is generated automatically and cannot be edited.
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
	The label of the IP. It is unique, and it is used to form the
	<code>ip_subdomain</code>. Can be used to call API functions.
	"""
	ip_label = None;

	"""
	Created automatically based on <code>ip_label</code>. It is a unique
	reference to the IP object.
	"""
	ip_subdomain = None;

	"""
	Reserved for future use.
	"""
	ip_lease_expires = None;

	"""
	ISO 8601 timestamp which holds the date and time when the IP was edited.
	Example format: 2013-11-29T13:00:01Z.
	"""
	ip_updated_timestamp = None;

	"""
	Primary IPs are the ones served by DHCP.
	"""
	ip_is_primary = None;

	"""
	Represents the Subnet this IP is allocated from.
	"""
	subnet_id = None;

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
