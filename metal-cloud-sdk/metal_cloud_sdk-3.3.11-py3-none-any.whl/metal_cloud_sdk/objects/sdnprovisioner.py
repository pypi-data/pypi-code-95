# -*- coding: utf-8 -*-

class SDNProvisioner(object):
	"""
	Holds constants used when SDN provisioning.
	"""

	def __init__(self, WANVLANRange, LANVLANRange, SANVLANRange, type):
		self.WANVLANRange = WANVLANRange;
		self.LANVLANRange = LANVLANRange;
		self.SANVLANRange = SANVLANRange;
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
	Port ranges for SAN VLANs. The two extremities are separated by '-'. For
	example: 300-399.
	"""
	SANVLANRange = None;

	"""
	The schema type.
	"""
	type = None;
