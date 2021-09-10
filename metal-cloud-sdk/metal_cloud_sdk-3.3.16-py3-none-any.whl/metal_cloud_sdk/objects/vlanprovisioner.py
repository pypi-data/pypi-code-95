# -*- coding: utf-8 -*-

class VLANProvisioner(object):
	"""
	Holds constants used when VLAN provisioning.
	"""

	def __init__(self, WANVLANRange, LANVLANRange, type):
		self.WANVLANRange = WANVLANRange;
		self.LANVLANRange = LANVLANRange;
		self.type = type;


	"""
	The quarantine VLAN ID.
	"""
	quarantineVLANID = 5;

	"""
	Port ranges for WAN VLANs. The two extremities are separated by '-'. For
	example: 100-199.
	"""
	WANVLANRange = None;

	"""
	Port ranges for LAN VLANs. The two extremities are separated by '-'. For
	example: 200-299.
	"""
	LANVLANRange = None;

	"""
	The schema type.
	"""
	type = None;
