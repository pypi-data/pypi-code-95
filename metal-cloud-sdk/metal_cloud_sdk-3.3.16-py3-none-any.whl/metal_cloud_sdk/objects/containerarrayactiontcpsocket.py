# -*- coding: utf-8 -*-

class ContainerArrayActionTCPSocket(object):
	"""
	ContainerArray action that uses tests the state of TCP sockets to asses the
	readiness or liveness of the Containers.
	"""

	def __init__(self, action_port):
		self.action_port = action_port;


	"""
	Port to access on the Container.
	"""
	action_port = None;

	"""
	The schema type.
	"""
	type = None;
