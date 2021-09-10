# -*- coding: utf-8 -*-

class RDP(object):
	"""
	RDP credentials for the installed OS.
	"""

	def __init__(self):
		pass;


	"""
	The port used to connect through RDP.
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
	The schema type
	"""
	type = None;
