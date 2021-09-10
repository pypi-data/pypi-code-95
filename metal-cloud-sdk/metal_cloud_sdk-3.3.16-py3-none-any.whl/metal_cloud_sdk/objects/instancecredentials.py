# -*- coding: utf-8 -*-

class InstanceCredentials(object):
	"""
	Information needed to connect to the server via IPMI, iLO etc.
	"""

	def __init__(self):
		pass;


	"""
	SSH credentials.
	"""
	ssh = None;

	"""
	RDP credentials.
	"""
	rdp = None;

	"""
	Deprecated, always null.
	"""
	ipmi = None;

	"""
	Reserved for future use.
	"""
	telnet = None;

	"""
	Deprecated, always null. iLO admin software panel credentials.
	"""
	ilo = None;

	"""
	Deprecated, always null. iDRAC admin software panel credentials.
	"""
	idrac = None;

	"""
	iSCSI initiator credentials.
	"""
	iscsi = None;

	"""
	Information needed to connect to the server via RemoteConsole
	"""
	remote_console = None;

	"""
	<a:schema>iSCSI</a:schema> objects. Shared drive credentials for all the
	shared drives an instance is attached to. The shared drives are grouped by
	their labels.
	"""
	shared_drives = [];

	"""
	<a:schema>IP</a:schema> addresses (can be <code>SUBNET_TYPE_IPV4</code> or
	<code>SUBNET_TYPE_IPV6</code>).
	"""
	ip_addresses_public = [];

	"""
	<a:schema>IP</a:schema> addresses (can be <code>SUBNET_TYPE_IPV4</code> or
	<code>SUBNET_TYPE_IPV6</code>). Are only allowed on LAN.
	"""
	ip_addresses_private = [];

	"""
	The schema type
	"""
	type = None;
