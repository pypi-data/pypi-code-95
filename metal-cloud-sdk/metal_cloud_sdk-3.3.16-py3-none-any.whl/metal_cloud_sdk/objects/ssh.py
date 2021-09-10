# -*- coding: utf-8 -*-

class SSH(object):
	"""
	SSH credentials for the installed OS.
	"""

	def __init__(self, initial_ssh_keys):
		self.initial_ssh_keys = initial_ssh_keys;


	"""
	The port used to connect through SSH.
	"""
	port = None;

	"""
	Administrator account. Only defined for Drives created from a template with
	an installed OS.
	"""
	username = None;

	"""
	Administrator account's initial password. Only defined for Drives created
	from a template with an installed OS.
	"""
	initial_password = None;

	"""
	The SSH keys (<a:schema>SSHKey</a:schema> objects) of all the users that had
	access to the <a:schema>Drive</a:schema> when disk space was allocated.
	Applicable only to Linux OS's created from a Linux template.
	"""
	initial_ssh_keys = {};

	"""
	The schema type
	"""
	type = None;
