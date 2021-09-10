# -*- coding: utf-8 -*-

class ContainerArrayActionHTTPGet(object):
	"""
	ContainerArray action that uses HTTP Get requests to asses the readiness or
	liveness of the Containers.
	"""

	def __init__(self, action_port):
		self.action_port = action_port;


	"""
	Path to acccess on the HTTP server.
	"""
	action_path = "/";

	"""
	Port to access on the Container.
	"""
	action_port = None;

	"""
	Host name to connect to. Defaults to the Container IP.
	"""
	action_host = None;

	"""
	Scheme to use for connecting to the host.
	"""
	action_scheme = "HTTP";

	"""
	The schema type.
	"""
	type = None;
