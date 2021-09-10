# -*- coding: utf-8 -*-

class VPLSProvisioner(object):
	"""
	Holds constants used when VPLS provisioning.
	"""

	def __init__(self, SANACLRange, ToRLANVLANRange, ToRSANVLANRange, ToRWANVLANRange, NorthWANVLANRange, type):
		self.SANACLRange = SANACLRange;
		self.ToRLANVLANRange = ToRLANVLANRange;
		self.ToRSANVLANRange = ToRSANVLANRange;
		self.ToRWANVLANRange = ToRWANVLANRange;
		self.NorthWANVLANRange = NorthWANVLANRange;
		self.type = type;


	"""
	The quarantine VLAN ID.
	"""
	quarantineVLANID = 5;

	"""
	ACL SAN ID.
	"""
	ACLSAN = 3999;

	"""
	ACL WAN ID.
	"""
	ACLWAN = 3399;

	"""
	ID ranges for SAN ACLs. The two extremities are separated by '-'. For
	example: 3700-3998.
	"""
	SANACLRange = None;

	"""
	Port ranges for ToR LAN VLANs. The two extremities are separated by '-'. For
	example: 400-699.
	"""
	ToRLANVLANRange = None;

	"""
	Port ranges for ToR SAN VLANs. The two extremities are separated by '-'. For
	example: 700-999.
	"""
	ToRSANVLANRange = None;

	"""
	Port ranges for ToR WAN VLANs. The two extremities are separated by '-'. For
	example: 100-399.
	"""
	ToRWANVLANRange = None;

	"""
	Port ranges for North WAN VLANs. The two extremities are separated by '-'.
	For example: 1001-2000.
	"""
	NorthWANVLANRange = None;

	"""
	The schema type.
	"""
	type = None;
