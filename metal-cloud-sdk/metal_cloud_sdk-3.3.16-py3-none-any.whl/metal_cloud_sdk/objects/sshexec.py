# -*- coding: utf-8 -*-

class SSHExec(object):
	"""
	Execute a command on a remote server using the SSH exec functionality (not
	through a shell).
	"""

	def __init__(self, command, ssh_target, type):
		self.command = command;
		self.ssh_target = ssh_target;
		self.type = type;


	"""
	Command line with arguments. For example: curl --help
	"""
	command = None;

	"""
	SSH client options such as the host, port, user, password, private keys,
	etc.
	"""
	ssh_target = None;

	"""
	Timeout in seconds. If the command does not finish within the alloted time
	the SSH connection is terminated.
	"""
	timeout = 1800;

	"""
	The schema type
	"""
	type = None;
