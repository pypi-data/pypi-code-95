# -*- coding: utf-8 -*-

class ContainerArrayStatus(object):
	"""
	A ContainerArrayStatus contains the status of the ContainerArray.
	"""

	def __init__(self):
		pass;


	"""
	The number of running containers.
	"""
	status_containers_running = None;

	"""
	The number of running containers that passed the readiness check.
	"""
	status_containers_ready = None;

	"""
	The schema type.
	"""
	type = None;
