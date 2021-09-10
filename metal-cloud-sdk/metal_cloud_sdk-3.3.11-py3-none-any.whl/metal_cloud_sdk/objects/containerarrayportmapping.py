# -*- coding: utf-8 -*-

class ContainerArrayPortMapping(object):
	"""
	ContainerArray port resource that facilitates inter-container and external
	communication.
	"""

	def __init__(self, port_mapping_name, port_mapping_container_port):
		self.port_mapping_name = port_mapping_name;
		self.port_mapping_container_port = port_mapping_container_port;


	"""
	Port resource name.
	"""
	port_mapping_name = None;

	"""
	Port the application inside the container listens to. May be used for
	inter-container communication.
	"""
	port_mapping_container_port = None;

	"""
	Port the container must be accessible on from external sources. May be used
	for external communication.
	"""
	port_mapping_service_port = None;

	"""
	Port communication protocol.
	"""
	port_mapping_protocol = "TCP";

	"""
	The schema type.
	"""
	type = None;
