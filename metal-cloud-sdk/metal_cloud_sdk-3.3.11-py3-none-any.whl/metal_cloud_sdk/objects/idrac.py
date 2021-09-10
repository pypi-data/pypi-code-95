# -*- coding: utf-8 -*-

class iDRAC(object):
	"""
	iDRAC control panel credentials. iDRAC is a control panel for Dell servers.
	The iDRAC card has a separate network connection and its own IP address.
	"""

	def __init__(self):
		pass;


	"""
	URL for the server's administration interface.
	"""
	control_panel_url = None;

	"""
	The username for the server's administration interface.
	"""
	username = None;

	"""
	The initial password for the server's administration interface.
	"""
	initial_password = None;

	"""
	The schema type
	"""
	type = None;
