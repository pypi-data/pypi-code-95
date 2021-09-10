# -*- coding: utf-8 -*-

class RemoteConsole(object):
	"""
	Information needed to connect to the server via Guacamole
	"""

	def __init__(self):
		pass;


	"""
	Protocol available. This property is not editable.
	"""
	remote_protocol = None;

	"""
	Tunnel path URL. This property is not editable.
	"""
	tunnel_path_url = None;

	"""
	Query string. This property is not editable.
	"""
	remote_control_panel_url = None;

	"""
	The schema type
	"""
	type = None;
