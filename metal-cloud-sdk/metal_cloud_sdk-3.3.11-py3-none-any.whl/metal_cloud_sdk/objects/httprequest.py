# -*- coding: utf-8 -*-

class HTTPRequest(object):
	"""
	A HTTP request definition compatible with the standard Web Fetch API.
	"""

	def __init__(self, url, type):
		self.url = url;
		self.type = type;


	"""
	For example: https://api.dummy.com/something?m=3. Template-like variables
	are supported:
	https://${{instance_subdomain_permanent}}/some-app-endpoint/?key=${{secret_id_of_something}}
	"""
	url = None;

	"""
	Web Fetch API options such as the HTTP method (GET, PUT, POST, DELETE,
	etc.), body, headers, etc.
	"""
	options = None;

	"""
	The schema type
	"""
	type = None;
