# -*- coding: utf-8 -*-

class SCPResourceLocation(object):
	"""
	A file path and SSH client connection options for use with Secure Copy
	Protocol (SCP).
	"""

	def __init__(self, path, ssh_target, type):
		self.path = path;
		self.ssh_target = ssh_target;
		self.type = type;


	"""
	For example: /home/someuser/.ssh/id_rsa.pub. Template-like variables are
	supported: /home/${{instance_credentials_user}}/.ssh/id_rsa.pub
	"""
	path = None;

	"""
	SSH client options such as the host, port, user, password, private keys,
	etc.
	"""
	ssh_target = None;

	"""
	The schema type
	"""
	type = None;
