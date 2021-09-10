# -*- coding: utf-8 -*-

class SambaServer(object):
	"""
	Samba server connection information.
	"""

	def __init__(self, samba_server_ip, samba_server_username, samba_server_password):
		self.samba_server_ip = samba_server_ip;
		self.samba_server_username = samba_server_username;
		self.samba_server_password = samba_server_password;


	"""
	Samba server's hostname.
	"""
	samba_server_hostname = None;

	"""
	Samba server's Windows kit share name.
	"""
	samba_server_windows_kit_share_name = None;

	"""
	Samba server's ip.
	"""
	samba_server_ip = None;

	"""
	Samba server's username.
	"""
	samba_server_username = None;

	"""
	Samba server's password.
	"""
	samba_server_password = None;

	"""
	The schema type
	"""
	type = None;
