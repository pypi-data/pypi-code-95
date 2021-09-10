# -*- coding: utf-8 -*-

class iSCSI(object):
	"""
	Target IQN, IP address, port number and the LUN ID.
	"""

	def __init__(self):
		pass;


	"""
	IQN of target iSCSI.
	"""
	target_iqn = None;

	"""
	iSCSI server IP address.
	"""
	storage_ip_address = None;

	"""
	Server listening port number.
	"""
	storage_port = None;

	"""
	Storage LUN ID.
	"""
	lun_id = None;

	"""
	The schema type
	"""
	type = None;
