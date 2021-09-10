# -*- coding: utf-8 -*-

class SecureGatewayBackend(object):
	"""
	Contains information regarding the backend proxied by secure gateway
	"""

	def __init__(self, name, ip, port, check_enabled, ssl_enabled):
		self.name = name;
		self.ip = ip;
		self.port = port;
		self.check_enabled = check_enabled;
		self.ssl_enabled = ssl_enabled;


	"""
	The name of the backend
	"""
	name = None;

	"""
	The IP of the backend
	"""
	ip = None;

	"""
	The port of the backend
	"""
	port = None;

	"""
	Should Secure Gateway send probes to check if this backend is working?
	"""
	check_enabled = None;

	"""
	Should Secure Gateway send SSL encrypted requests to the backend?
	"""
	ssl_enabled = None;

	"""
	The schema type
	"""
	type = None;
