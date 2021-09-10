# -*- coding: utf-8 -*-

class WebProxy(object):
	"""
	Web proxy connection information.
	"""

	def __init__(self, web_proxy_server_ip, web_proxy_server_port):
		self.web_proxy_server_ip = web_proxy_server_ip;
		self.web_proxy_server_port = web_proxy_server_port;


	"""
	Web proxy's server IP.
	"""
	web_proxy_server_ip = None;

	"""
	Web proxy's port.
	"""
	web_proxy_server_port = None;

	"""
	Web proxy's username.
	"""
	web_proxy_username = None;

	"""
	Web proxy's password.
	"""
	web_proxy_password = None;

	"""
	The schema type
	"""
	type = None;
