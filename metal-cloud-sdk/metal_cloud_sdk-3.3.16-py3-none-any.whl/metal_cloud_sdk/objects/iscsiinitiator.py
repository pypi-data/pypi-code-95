# -*- coding: utf-8 -*-

class iSCSIInitiator(object):
	"""
	Initiator IQN, username and password and other iSCSI connection details.
	"""

	def __init__(self):
		pass;


	"""
	The iSCSI username.
	"""
	username = None;

	"""
	The iSCSI initial password.
	"""
	password = None;

	"""
	IQN of initiator iSCSI.
	"""
	initiator_iqn = None;

	"""
	IPv4 gateway in decimal dotted notation.
	"""
	gateway = None;

	"""
	IPv4 dotted decimal notation netmask.
	"""
	netmask = None;

	"""
	iSCSI client IP address.
	"""
	initiator_ip_address = None;

	"""
	The schema type
	"""
	type = None;
