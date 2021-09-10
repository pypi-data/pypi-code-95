# -*- coding: utf-8 -*-

class SecureGatewayPeer(object):
	"""
	Secure gateway node metadata
	"""

	def __init__(self, name, IP, port, privateSSHKey):
		self.name = name;
		self.IP = IP;
		self.port = port;
		self.privateSSHKey = privateSSHKey;


	"""
	Node name. It's how haproxy finds nodes in a cluster
	"""
	name = None;

	"""
	Node IP. It's how ansible connects to each pear
	"""
	IP = None;

	"""
	The port used by haproxy peers to sync stick tables
	"""
	port = None;

	"""
	SSH private key used to allow BSI to connect with ansible
	"""
	privateSSHKey = None;

	"""
	The schema type.
	"""
	type = None;
