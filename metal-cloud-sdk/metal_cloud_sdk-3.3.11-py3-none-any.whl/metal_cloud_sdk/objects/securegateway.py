# -*- coding: utf-8 -*-

class SecureGateway(object):
	"""
	Secure gateway instance metadata
	"""

	def __init__(self, domain, VRRPIP, datacenterName, SSLCrtFilePath):
		self.domain = domain;
		self.VRRPIP = VRRPIP;
		self.datacenterName = datacenterName;
		self.SSLCrtFilePath = SSLCrtFilePath;


	"""
	The DNS domain pointing to a secure gateway cluster
	"""
	domain = None;

	"""
	VRRP IP pointing to secure gateway cluster
	"""
	VRRPIP = None;

	"""
	The datacenter used for this secure gateway cluster
	"""
	datacenterName = None;

	"""
	The path where SSL certificate is stored
	"""
	SSLCrtFilePath = None;

	"""
	The schema type.
	"""
	type = None;

	"""
	The ID of the server. It is automatically generated and cannot be edited.
	"""
	ID = None;

	"""
	An array with all the reserved ports
	"""
	reservedPorts = [];

	"""
	An array with all the peers
	"""
	peers = [];
